using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
public enum VehicleState
{
    SEEK, FLEE, PURSUIT, OFFSET_PURSUIT, ARRIVAL
}

public class VehicleBehaviour : MonoBehaviour {
    static float mass = 1;
    static float inverseMass = 1 / mass;

    const float maxForce = 10;
    const float maxSpeed = 100;

    public Vector2 position = Vector2.zero;
    public Vector2 velocity = Vector2.zero;

    public Vector2 forward;
    public Vector2 side;
    
    public Vector2 steering;
    
    public VehicleState state;

    public GameManager 

    void Awake()
    {

    }


    void FixedUpdate()
    {
        var steeringForce = Vector2.ClampMagnitude(steering, maxForce);
        var acceleration = steeringForce * inverseMass;
        velocity = Vector2.ClampMagnitude(velocity + acceleration, maxSpeed);
        position += velocity;

        forward = velocity.normalized;
        side = Vector2.Perpendicular(forward);

    }

    private void Seek(Vector2 target)
    {
        var desiredVelocity = (position - target).normalized * maxSpeed;
        steering = desiredVelocity - velocity;
    }

    private void Flee(Vector2 target)
    {
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
        const float slowing_distance = 100;
        Vector2 target_offset = target - position;
        float distance = target_offset.magnitude;
        float ramped_speed = maxSpeed * (distance / slowing_distance);
        float clipped_speed = Mathf.Min(ramped_speed, maxSpeed);
        Vector2 desired_velocity = (clipped_speed / distance) * target_offset;
        steering = desired_velocity - velocity;
    }

    private Vector2 EstimateFuturePosition(VehicleBehaviour quarry)
    {        
        float distanceFactor = (position - quarry.position).magnitude;
        /// @TODO: need to check the angle factor definition. 
        /// Goal is that T should tend to 0 when we are aiming at a target and they are also
        /// aiming towards us...
        float dot = Vector2.Dot(forward, quarry.forward);
        float angleFactor = (dot + 1) / 2; 

        float T = distanceFactor * angleFactor;
        // project the quarry's velocity (scaled by T) to estimate the future positiion.
        return quarry.position + quarry.velocity * T;
    }

    private void Evasion(VehicleBehaviour quarry)
    {
        Vector2 target = EstimateFuturePosition(quarry);
        Flee(target);
    }

    // Use this for initialization
    void Start () {
		
	}
	
	// Update is called once per frame
	void Update () {
		
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