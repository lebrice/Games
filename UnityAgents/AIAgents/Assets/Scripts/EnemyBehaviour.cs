using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class EnemyBehaviour : MonoBehaviour {
    public float movementSpeed = 1.0f;
    private void Awake()
    {
    }

    // Use this for initialization
    void Start () {
		
	}
	
	// Update is called once per frame
	void Update () {
        this.transform.position += this.transform.forward * Time.deltaTime * this.movementSpeed;
    }

    private void FixedUpdate()
    {
    }
    
    private void OnTriggerEnter(Collider other)
    {
        Debug.Log("Enemy just triggered with " + other.tag);
        if (other.tag == "MiddleObstacle")
        {

        }
    }
}
