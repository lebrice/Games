using System.Collections;
using System.Collections.Generic;
using UnityEngine;

[RequireComponent(typeof(AudioSource))]
public class PortalBehaviour : MonoBehaviour {
    /// <summary>
    /// Sound effect played when the portal is used.
    /// </summary>
    public AudioClip teleportSoundEffect;

    /// <summary>
    /// Other portal to teleport you to.
    /// </summary>
    public PortalBehaviour destination;


    private AudioSource source;

    private float volLowRange = .5f;
    private float volHighRange = 1.0f;

    void Awake()
    {
        source = GetComponent<AudioSource>();
    }

    public static int SpawnOffset = 1;
	// Use this for initialization
	void Start () {
		
	}
	
	// Update is called once per frame
	void Update () {
		
	}

    private void OnTriggerEnter(Collider other)
    {
        if(other.tag == "Player" || other.tag == "Enemy"){
            Debug.Log(other.tag + " just stepped into a portal.");
            var position = this.destination.transform.position;
            var direction = this.destination.transform.forward;
            var spawnPoint = position + SpawnOffset * direction;
            spawnPoint.y = other.transform.position.y;

            other.transform.SetPositionAndRotation(spawnPoint, this.destination.transform.rotation);


            float vol = Random.Range(volLowRange, volHighRange);
            source.PlayOneShot(teleportSoundEffect, vol);
        }
        else if (other.tag == "Agent")
        {
            Debug.Log("Agent is tryign to use the portal!");
        }
    }
}
