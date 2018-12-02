using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class DoorBehaviour : MonoBehaviour {
    
    void Awake()
    {
    }
    
    // Use this for initialization
    void Start () {
		
	}
	
	// Update is called once per frame
	void Update () {
		
	}

    

    private void OnTriggerEnter2D(Collider2D other)
    {
        //Debug.Log(name + " was triggered by" + other.name);
        if (other.CompareTag("Vehicle"))
        {
            var circleCollider = other.GetComponent<CircleCollider2D>();
            if(other == circleCollider)
            {
                var agent = other.GetComponent<VehicleBehaviour>();
                GameManager.instance.AgentReachedDoor(agent, gameObject);
            }
        }
    }
}
