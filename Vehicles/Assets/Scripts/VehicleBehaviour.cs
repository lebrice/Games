
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;

public enum VehicleState
{
    STILL,
    SEEK,
    FLEE,
    PURSUIT,
    OFFSET_PURSUIT,
    ARRIVAL,
    COLLISION_AVOIDANCE,
    WANDERING,
    BLOCK,
    CONVERSATION,
}

public enum AgentRole
{
    Traveller,
    Wanderer,
    Social,
    None,
}
public class VehicleBehaviour : MonoBehaviour
{
    public const float maxForce = 10f;

    public float maxSteeringForce = 5f;
    public float maxBrakingForce = 10f;
    public float maxSpeed = 5f;

    //public Vector2 position = Vector2.zero;
    //public Vector2 velocity = Vector2.zero;

    public static float radius = 0.5f;
    [HideInInspector]
    public Vector2 forward;
    [HideInInspector]
    public Vector2 side;



    public VehicleState state = VehicleState.STILL;
    public VehicleState previousState = VehicleState.STILL;

    public AgentRole role;
    [HideInInspector]
    public Rigidbody2D rigidBody;
    private SpriteRenderer spriteRenderer;
    private CircleCollider2D circleCollider;
    protected BoxCollider2D boxCollider;
    public Vector2 target;

    public List<Collider2D> collisionAvoidanceObjects;
    private float sightLength;

    public void Awake()
    {
        //collisions = new Collider2D[100];
        collisionAvoidanceObjects = new List<Collider2D>();
        rigidBody = GetComponent<Rigidbody2D>();
        spriteRenderer = GetComponent<SpriteRenderer>();
        circleCollider = GetComponent<CircleCollider2D>();
        radius = circleCollider.radius;
        boxCollider = GetComponent<BoxCollider2D>();
    }

    // Use this for initialization
    protected virtual void Start()
    {
        Debug.Log("Agent '" + name + "' Starting at position" + transform.position + " My role is: " + role.ToString());
    }

    protected void SetColor(Color color)
    {
        spriteRenderer.color = color;
    }
    
    protected virtual void FixedUpdate()
    {
        if (role == AgentRole.None || state == VehicleState.STILL)
        {
            rigidBody.velocity = Vector2.zero;
            return;
        }
        foreach (var otherCollider in collisionAvoidanceObjects)
        {
            CollisionAvoidance(otherCollider);
        }
        //Debug.Log("Role: " + role + " Target: " + target + " Steering: " + steering);
        rigidBody.velocity = Vector2.ClampMagnitude(rigidBody.velocity, maxSpeed);
        // update the line of sight length based on velocity.
        UpdateLineOfSightLength();

        var position = transform.position;
        Vector2 velocity = rigidBody.velocity;

        var angle = Mathf.Atan2(velocity.y, velocity.x) * Mathf.Rad2Deg;
        transform.rotation = Quaternion.AngleAxis(angle, Vector3.forward);
    }


    protected void Seek(Vector2 target)
    {
        Vector2 position = transform.position;
        Vector2 velocity = rigidBody.velocity;
        var desiredVelocity = (target - position).normalized * maxSpeed;
        var steeringForce = desiredVelocity - velocity;
        steeringForce = Vector2.ClampMagnitude(steeringForce, maxForce);
        AddForce(steeringForce, maxForce);
        Debug.DrawRay(transform.position, steeringForce, Color.green, 0.2f);
    }

    protected void Flee(Vector2 target)
    {
        Vector2 position = transform.position;
        Vector2 velocity = rigidBody.velocity;
        var desiredVelocity = (target - position).normalized * maxSpeed;
        var steeringForce = desiredVelocity - velocity;
        steeringForce = Vector2.ClampMagnitude(steeringForce, maxForce);
        AddForce(steeringForce, maxSteeringForce);
        Debug.DrawRay(transform.position, steeringForce, Color.green, 0.2f);
    }

    protected void Pursuit(VehicleBehaviour quarry)
    {
        Vector2 target = EstimateFuturePosition(quarry);
        Seek(target);
    }

    protected void Wander()
    {
        // Choose a random unobstructed point as a target, and travel there.
        // Once we come close enough to it, choose another target and repeat.
        Arrival(target);
        if (CloserThanThreshold(transform.position, target, 1.0f))
        {
            Debug.Log(name + " is selecting a new target:" + target);
            SelectRandomTarget();
        }
    }


    protected virtual void OffsetPursuit(VehicleBehaviour other, float radius, float offsetAngle = 90)
    {
        Vector2 futurePosition = EstimateFuturePosition(other);
        var offset = (Vector2.right * radius).Rotate(offsetAngle);
        target = futurePosition + offset;
        Seek(target);
    }

    protected void Arrival(Vector2 target)
    {
        const float slowing_distance = 2;
        Vector2 position = transform.position;
        Vector2 velocity = rigidBody.velocity;

        Vector2 target_offset = target - position;
        float distance = target_offset.magnitude;
        float ramped_speed = maxSpeed * (distance / slowing_distance);
        float clipped_speed = Mathf.Min(ramped_speed, maxSpeed);
        Vector2 desired_velocity = (clipped_speed / distance) * target_offset;

        var steeringForce = desired_velocity - velocity;
        AddForce(steeringForce, maxSteeringForce);
        Debug.DrawRay(transform.position, steeringForce, Color.green, 0.2f);
    }

    protected Vector2 EstimateFuturePosition(VehicleBehaviour other)
    {

        Vector2 position = transform.position;
        Vector2 velocity = rigidBody.velocity;
        Vector2 otherPosition = other.transform.position;
        Vector2 otherVelocity = other.rigidBody.velocity;
        float distance = Vector2.Distance(position, otherPosition);
        /// @TODO: need to check the angle factor definition. 
        /// Goal is that T should tend to 0 when we are aiming at a target and they are also
        /// aiming towards us...
        //float dot = Vector2.Dot(transform.right, other.transform.right);
        //float angleFactor = (dot + 1) / 2;
        //float T = distanceFactor * angleFactor;
        float t = distance;
        // project the quarry's velocity (scaled by T) to estimate the future positiion.
        return otherPosition + otherVelocity * t;
    }

    protected void Evasion(VehicleBehaviour quarry)
    {
        Vector2 target = EstimateFuturePosition(quarry);
        Flee(target);
    }

    private void UpdateLineOfSightLength()
    {
        sightLength = Mathf.Max(3, rigidBody.velocity.magnitude);
        sightLength = Mathf.FloorToInt(sightLength);
        // only update when the value actually changes.
        if (boxCollider.offset.x != sightLength)
        {
            boxCollider.offset = new Vector2(sightLength / 2, 0);
            boxCollider.size = new Vector2(sightLength, 1);
        }
    }
    protected void AddForce(Vector2 force, float maxForce = maxForce)
    {
        force = Vector2.ClampMagnitude(force, maxForce);
        rigidBody.AddForce(force, ForceMode2D.Force);
    }

    protected IEnumerable<VehicleBehaviour> AgentsWithinRadius(float radius, System.Func<VehicleBehaviour, bool> predicate)
    {
        var thresholdSquared = Mathf.Pow(radius, 2);
        Vector2 position = transform.position;
        var vehicles = GameManager.instance.vehicles
            .Where(v => predicate(v))
            .Select(v => System.Tuple.Create(v, ((Vector2)v.transform.position - position).sqrMagnitude))
            .Where((t, distance) =>
            {
                return t.Item2 <= thresholdSquared;
            })
            .OrderBy(t => t.Item2)
            .Select(t => t.Item1);
        return vehicles;
    }

    protected void SelectRandomTarget()
    {
        target = GameManager.instance.GetUnobstructedRegionForAgent();
    }

    protected virtual void OnTriggerEnter2D(Collider2D other)
    {
        //Debug.Log(name + " was triggered by" + other.name);
        if (other.CompareTag("Obstacle") || other.CompareTag("Vehicle") || other.CompareTag("Wall"))
        {
            collisionAvoidanceObjects.Add(other);
            //if (state != VehicleState.COLLISION_AVOIDANCE)
            //{
            //    previousState = state;
            //}
            //state = VehicleState.COLLISION_AVOIDANCE;
        }
    }

    protected virtual void OnTriggerExit2D(Collider2D other)
    {
        collisionAvoidanceObjects.Remove(other);
        //if (collisionAvoidanceObjects.Count == 0)
        //{
        //    state = previousState;
        //}
    }

    protected virtual void TriggerStay2D(Collider2D other)
    {
    }

    protected virtual void CollisionAvoidance(Collider2D other)
    {
        //Debug.Log("Collision Avoidance between " + name + " and: " + other.name);
        var distance = circleCollider.Distance(other);
        var force = distance.normal * distance.distance * maxForce;
        Debug.DrawRay(transform.position, force, Color.blue, 0.2f);

        AddForce(force);

        //Vector2 closestPointOther = distance.pointB;
        //Vector2 position = transform.position;
        //var toObstacle = closestPointOther - position;
        //var projection = Vector2.Dot(toObstacle, transform.up);

        //var scalingFactor = projection * (1 / Mathf.Max(toObstacle.magnitude, 0.1f));
        //Vector2 steeringCA = -transform.up * scalingFactor * maxForce;
        //steeringCA = Vector2.ClampMagnitude(steeringCA, maxForce);
        //AddForce(steeringCA, maxForce/2);
        //Debug.DrawRay(transform.position, steeringCA, Color.blue, 0.2f);


        //var brakingFactor = 0.1f * Mathf.Max(rigidBody.velocity.sqrMagnitude, 0.1f);
        //Vector2 brakingForce = -1 * brakingFactor * transform.right;
        //// The braking force is clamped higher than the steering and turning forces.
        //brakingForce = Vector2.ClampMagnitude(brakingForce, 2 * maxForce);
        //AddForce(brakingForce);
        //Debug.DrawRay(transform.position, brakingForce, Color.cyan, 0.2f);
    }

    // Update is called once per frame
    protected virtual void Update()
    {
        Debug.DrawRay(transform.position, rigidBody.velocity, color: Color.black, duration: 0.5f);
    }

    public static bool CloserThanThreshold(Vector2 a, Vector2 b, float threshold, bool thresholdIsSquared = false)
    {
        return (b - a).sqrMagnitude < (thresholdIsSquared ? threshold : Mathf.Pow(threshold, 2));
    }
}

/// <summary>
/// Taken from https://answers.unity.com/questions/661383/whats-the-most-efficient-way-to-rotate-a-vector2-o.html
/// </summary>
public static class Vector2Extension
{
    public static Vector2 Rotate(this Vector2 v, float degrees)
    {
        return Quaternion.Euler(0, 0, degrees) * v;
        //float sin = Mathf.Sin(degrees * Mathf.Deg2Rad);
        //float cos = Mathf.Cos(degrees * Mathf.Deg2Rad);

        //float tx = v.x;
        //float ty = v.y;
        //v.x = (cos * tx) - (sin * ty);
        //v.y = (sin * tx) + (cos * ty);
        //return v;
    }

  
}
