using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class CollectibleBehaviour : MonoBehaviour {

	// Use this for initialization
	void Start () {
		
	}
	
	// Update is called once per frame
	void Update () {
		
	}

    private void OnTriggerEnter(Collider other)
    {
        if (other.tag == "Player" || other.tag == "Agent")
        {
            Debug.Log(other.name + " Just grabbed a coin!");
            this.gameObject.SetActive(false);
        }
    }
}
