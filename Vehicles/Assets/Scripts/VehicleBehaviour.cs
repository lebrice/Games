using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public enum VehicleState
{
    SEEK, FLEE, PURSUIT, OFFSET_PURSUIT, ARRIVAL
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


    public float maxForce = 10f;
    public float maxSpeed = 5f;

    //public Vector2 position = Vector2.zero;
    //public Vector2 velocity = Vector2.zero;

    public static float radius = 0.5f;
    [HideInInspector]
    public Vector2 forward;
    [HideInInspector]
    public Vector2 side;

    private Vector2 steering = Vector2.zero;
    private Vector2 steeringCollisionAvoidance = Vector2.zero;

    public VehicleState state;
    public AgentRole role;

    [HideInInspector]
    public Rigidbody2D rigidBody;
    private SpriteRenderer spriteRenderer;
    private CircleCollider2D circleCollider;
    private BoxCollider2D boxCollider;
    public Vector2 target;

    public void Awake()
    {
        rigidBody = GetComponent<Rigidbody2D>();
        spriteRenderer = GetComponent<SpriteRenderer>();
        circleCollider = GetComponent<CircleCollider2D>();
        radius = circleCollider.radius;
        boxCollider = GetComponent<BoxCollider2D>();
    }

    // Use this for initialization
    void Start()
    {
        spriteRenderer.color = GetColor();
        Debug.Log("Agent Starting. My role is:" + role.ToString() + " Target is " + target);
        gameObject.name = role.ToString();
    }

    private Color GetColor()
    {
        switch (role)
        {
            case AgentRole.Traveller:
                return Color.red;
            case AgentRole.Social:
                return Color.yellow;
            case AgentRole.Wanderer:
                return Color.green;
            default:
                return Color.white;
        }
    }

    void FixedUpdate()
    {
        if (role == AgentRole.None)
        {
            return;
        }
        else if (role == AgentRole.Traveller)
        {
            Seek(target);
        }
        var steeringForce = Vector2.ClampMagnitude(steering, maxForce);

        //Debug.Log("Role: " + role + " Target: " + target + " Steering: " + steering);
        rigidBody.velocity = Vector2.ClampMagnitude(rigidBody.velocity, maxSpeed);
        rigidBody.AddForce(steeringForce);
        Vector2 position = transform.position;
        Vector2 velocity = rigidBody.velocity;
        
        var angle = Mathf.Atan2(velocity.y, velocity.x) * Mathf.Rad2Deg;
        transform.rotation = Quaternion.AngleAxis(angle, Vector3.forward);

        //var acceleration = steeringForce * inverseMass;
        //velocity = Vector2.ClampMagnitude(velocity + acceleration, maxSpeed);
        //position += velocity * Time.deltaTime;
        //forward = velocity.normalized;
        //side = Vector2.Perpendicular(forward);

        //transform.position = position;
        //// because of the way "right" means the red axis.
        //transform.right = forward;
    }

    private void Seek(Vector2 target)
    {
        Vector2 position = transform.position;
        Vector2 velocity = rigidBody.velocity;
        var desiredVelocity = (target - position).normalized * maxSpeed;
        steering = desiredVelocity - velocity;
    }

    private void Flee(Vector2 target)
    {
        Vector2 position = transform.position;
        Vector2 velocity = rigidBody.velocity;
        var desiredVelocity = (target - position).normalized * maxSpeed;
        steering = desiredVelocity - velocity;
    }

    private void Pursuit(VehicleBehaviour quarry)
    {
        Vector2 target = EstimateFuturePosition(quarry);
        Seek(target);
    }

    private void OffsetPursuit(VehicleBehaviour quarry, float radius, float offsetAngle = 90)
    {
        Vector2 futurePosition = EstimateFuturePosition(quarry);
        var offset = (Vector2.right * radius).Rotate(offsetAngle);
        var target = futurePosition + offset;
        Seek(target);
    }

    private void Arrival(Vector2 target)
    {
        const float slowing_distance = 2;
        Vector2 position = transform.position;
        Vector2 velocity = rigidBody.velocity;

        Vector2 target_offset = target - position;
        float distance = target_offset.magnitude;
        float ramped_speed = maxSpeed * (distance / slowing_distance);
        float clipped_speed = Mathf.Min(ramped_speed, maxSpeed);
        Vector2 desired_velocity = (clipped_speed / distance) * target_offset;

        steering = desired_velocity - velocity;
    }

    private Vector2 EstimateFuturePosition(VehicleBehaviour quarry)
    {

        Vector2 position = transform.position;
        Vector2 velocity = rigidBody.velocity;
        Vector2 quarryPosition = quarry.transform.position;
        Vector2 quarryVelocity = quarry.rigidBody.velocity;
        float distanceFactor = (position - quarryPosition).magnitude;
        /// @TODO: need to check the angle factor definition. 
        /// Goal is that T should tend to 0 when we are aiming at a target and they are also
        /// aiming towards us...
        float dot = Vector2.Dot(forward, quarry.forward);
        float angleFactor = (dot + 1) / 2;

        float T = distanceFactor * angleFactor;
        // project the quarry's velocity (scaled by T) to estimate the future positiion.
        return quarryPosition + quarryVelocity * T;
    }

    private void Evasion(VehicleBehaviour quarry)
    {
        Vector2 target = EstimateFuturePosition(quarry);
        Flee(target);
    }
    private Collider2D[] collisions = new Collider2D[100];

    private void OnTriggerEnter2D(Collider2D other)
    {
        Debug.Log(name + " was triggered by" + other.name);
        if (other.CompareTag("Obstacle"))
        {
            //Debug.Log("About to hit an obstacle: " + other.name);
            CollisionAvoidance(other);
        }
    }

    private void TriggerStay2D(Collider2D other)
    {
        if (other.CompareTag("Obstacle"))
        {
            CollisionAvoidance(other);
        }
    }

    private void CollisionAvoidance(Collider2D other)
    {
        //Debug.Log("About to hit an obstacle: " + other.name);
        var center = other.transform.position;
        //var numCollisions = boxCollider.GetContacts(collisions);
        var toObstacle = other.transform.position - transform.position;
        var projection = Vector2.Dot(toObstacle, transform.right);

        var scalingFactor = projection * (5 / toObstacle.magnitude);
        Vector2 steeringCA = -transform.right * scalingFactor * maxForce;
        Debug.Log("SteeringCollisionAvoidance: " + steeringCA);

        steering += steeringCA;

        var obstacle = other.GetComponent<ObstacleBehaviour>();
        //var coll = collision.GetComponent<Collider2D>();
    }

    // Update is called once per frame
    void Update()
    {
        Debug.Log("Right: " +  transform.right + "Up: " + transform.up);
        Debug.DrawRay(transform.position, transform.right * 10, color: Color.black, duration: 0.5f);
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