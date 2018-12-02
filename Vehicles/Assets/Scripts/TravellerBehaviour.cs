using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class TravellerBehaviour : VehicleBehaviour {
    

	// Use this for initialization
	protected override void Start () {
        role = AgentRole.Traveller;
        state = VehicleState.SEEK;
        previousState = VehicleState.SEEK;
        SetColor(Color.red);
        base.Start();
	}

    protected override void FixedUpdate()
    {
        Arrival(target);
        base.FixedUpdate();
    }
}
