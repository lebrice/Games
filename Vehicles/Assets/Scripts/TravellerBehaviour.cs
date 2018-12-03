using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class TravellerBehaviour : VehicleBehaviour {
    

	// Use this for initialization
	protected override void Start () {
        StartCoroutine(Traveller());
        base.Start();
    }

    IEnumerator Traveller()
    {
        role = AgentRole.Traveller;
        state = VehicleState.SEEK;
        previousState = VehicleState.SEEK;
        SetColor(Color.red);
        while (true)
        {
            SelectDoorAtRandom();
            bool reachedDoor = false;
            while (!reachedDoor)
            {
                for (int i = 0; i < 10 && !reachedDoor; i++)
                {
                    yield return new WaitForSeconds(1);
                    reachedDoor = ReachedTarget();
                }
                if (!reachedDoor)
                {
                    SelectOtherDoor();
                }
            }
            RespawnAtRightDoor();
            GameManager.instance.travellerSuccessCount++;
        }
    }

    private void RespawnAtRightDoor()
    {
        transform.position = GameManager.instance.doorRight.transform.position;
        transform.rotation = Quaternion.Euler(new Vector3(0, 0, 180));
    }

    private void SelectDoorAtRandom()
    {
        var doorTop = GameManager.instance.doorLeftTop.position;
        var doorBottom = GameManager.instance.doorLeftBottom.position;
        target = Random.Range(0, 2) == 0 ? doorTop: doorBottom;
    }

    private void SelectOtherDoor()
    {
        Debug.Log(name + " decided to switch doors, since it was unable to reach one in time.");
        Vector2 doorTop = GameManager.instance.doorLeftTop.position;
        Vector2 doorBottom = GameManager.instance.doorLeftBottom.position;
        target = (target == doorTop) ? doorBottom : doorTop;
    }

    protected override void OnTriggerEnter2D(Collider2D other)
    {
        var vehicle = other.GetComponent<VehicleBehaviour>();
        if (vehicle != null)
        {
            return;
        }
        else
        {
            base.OnTriggerEnter2D(other);
        }
    }

    

    protected override void FixedUpdate()
    {
        if(collisionAvoidanceObjects.Count == 0)
        {
            
        }
        Seek(target);
        base.FixedUpdate();
    }
}
