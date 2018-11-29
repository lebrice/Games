using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class DoorBehaviour : MonoBehaviour {
    
    // Use this for initialization
    void Start () {
		
	}
	
	// Update is called once per frame
	void Update () {
		
	}

    private void OnTriggerEnter2D(Collider2D other)
    {
        if (other.CompareTag("Vehicle"))
        {
            Debug.Log(name + " was triggered by" + other.name);
            var agent = other.GetComponent<VehicleBehaviour>();
            GameManager.instance.AgentReachedDoor(agent, gameObject);
        }
    }
}
