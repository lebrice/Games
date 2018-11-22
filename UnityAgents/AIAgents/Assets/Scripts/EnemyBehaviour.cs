using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class EnemyBehaviour : MonoBehaviour
{

    public float movementSpeed = 1.0f;

    public GameObject lineOfSight;
    private BoxCollider lineOfSightBoxCollider;
    private MeshRenderer lineOfSightMeshRenderer;
    private bool isInsideObstacle;
    //private Random rnd = new Random();

        
    private void Awake()
    {
        this.lineOfSightBoxCollider = this.lineOfSight.GetComponent<BoxCollider>();
        this.lineOfSightMeshRenderer = this.lineOfSight.GetComponent<MeshRenderer>();
    }

    // Use this for initialization
    void Start()
    {

    }

    // Update is called once per frame
    void Update()
    {
        this.transform.position += this.transform.forward * Time.deltaTime * this.movementSpeed;

        isInsideObstacle = System.Math.Abs(this.transform.position.z) < 1.5;
        this.lineOfSightBoxCollider.enabled = !this.isInsideObstacle;
        this.lineOfSightMeshRenderer.enabled = !this.isInsideObstacle;
    }

    private void FixedUpdate()
    {
    }

    private void OnTriggerEnter(Collider other)
    {
        //Debug.Log("Enemy just got triggered by " + other.name);
        if (other.tag == "MiddleObstacle" && isInsideObstacle)
        {
            Debug.Log("Entering the Obstacle");
            var choice = Random.Range(0, 3);

            if (choice == 0)
            {
                Debug.Log("Choice: Despawning the enemy.");
                // de-shawn.
                this.gameObject.SetActive(false);
            }
            else if (choice == 1)
            {
                Debug.Log("Choice: Moving through unhindered.");
                // move through without any problem.
            }
            else if (choice == 2)
            {
                Debug.Log("Choice: Enemy is changing direction.");
                // change direction.
                this.transform.Rotate(new Vector3(0, 1, 0), 180);
            }
        }
    }

    //private void OnTriggerExit(Collider other)
    //{
    //    if (other.tag == "MiddleObstacle")
    //    {
    //        Debug.Log("Exiting the Obstacle");
    //        this.isInsideObstacle = false;
    //    }
    //}
}
