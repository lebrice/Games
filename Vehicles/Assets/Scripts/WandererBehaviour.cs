using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;

public class WandererBehaviour : VehicleBehaviour {

    public const float startBlockingTravellersThreshold = 2.0f;
    public const float stopBlockingTravellersThreshold = 3.0f;
    private VehicleBehaviour agentToBlock;
    
    // Use this for initialization
    protected override void Start()
    {
        role = AgentRole.Wanderer;
        state = VehicleState.WANDERING;
        previousState = VehicleState.WANDERING;
        SetColor(Color.green);
        base.Start();
        SelectRandomTarget();
        StartCoroutine(Wanderer());
    }

    IEnumerator Wanderer()
    {
        while (true)
        {
            state = VehicleState.WANDERING;
            yield return new WaitUntil(() => FindTravellerToBlock(out agentToBlock));
            state = VehicleState.BLOCK;
            yield return new WaitUntil(() => TravellerGotAway());
            SelectRandomTarget();
        }
    }
    
    protected override void FixedUpdate()
    {
        if(state == VehicleState.WANDERING)
        {
            Wander();
            // move slower while wandering.
            rigidBody.velocity = Vector2.ClampMagnitude(rigidBody.velocity, maxSpeed / 2);
        }
        else if (state == VehicleState.BLOCK)
        {
            Block(agentToBlock);
        }
        // disable the "field of view" when we're trying to block someone.
        boxCollider.enabled = (state != VehicleState.BLOCK);
        base.FixedUpdate();
    }



    private bool FindTravellerToBlock(out VehicleBehaviour agentToBlock)
    {
        agentToBlock = AgentsWithinRadius(
            startBlockingTravellersThreshold,
            v => v.role == AgentRole.Traveller && v.name != name
        ).FirstOrDefault();
        return agentToBlock != default(VehicleBehaviour);
    }

    private bool TravellerGotAway()
    {
        var travellerPosition = agentToBlock.transform.position;
        return !CloserThanThreshold(transform.position, travellerPosition, stopBlockingTravellersThreshold);
    }


    private void Block(VehicleBehaviour other)
    {
        //float otherOrientation = other.transform.rotation.z;

        var position = transform.position;
        Vector2 otherPosition = other.transform.position;
        var toTarget = (other.target - otherPosition).normalized;
        var angle = Vector2.SignedAngle(Vector2.right, toTarget);
        OffsetPursuit(other, startBlockingTravellersThreshold / 2, angle);

        // make sure that the wanderers don't block the exit completely (keep an offset from the doors.)
        var doorX = GameManager.instance.doorLeftTop.position.x;
        transform.position = new Vector3(Mathf.Max(doorX + 1, position.x), position.y, 0);
    }
}
