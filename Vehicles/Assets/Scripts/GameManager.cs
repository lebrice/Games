using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class GameManager : MonoBehaviour
{
    public const float xMin = -10f;
    public const float xMax = 10f;
    public const float yMin = -5f;
    public const float yMax = 5f;

    //Static instance of GameManager which allows it to be accessed by any other script.
    public static GameManager instance = null;
    [Range(2, 10)]
    public int numberOfObstacles = 2;
    [Range(1, 10)]
    public int numberOfWanderingAgents = 1;
    [Range(1, 10)]
    public int numberOfTravellingAgents = 1;

    public IList<VehicleBehaviour> vehicles = new List<VehicleBehaviour>();

    public VehicleBehaviour travellerPrefab;
    public ObstacleBehaviour obstaclePrefab;

    public Transform doorLeftTop;
    public Transform doorLeftBottom;
    public Transform doorRight;

    public List<GameObject> obstacles;

    //Awake is always called before any Start functions
    void Awake()
    {
        //Check if instance already exists
        if (instance == null)
        {
            //if not, set instance to this
            instance = this;
        }

        //If instance already exists and it's not this:
        else if (instance != this)
        {
            //Then destroy this. This enforces our singleton pattern, meaning there can only ever be one instance of a GameManager.
            Destroy(gameObject);
        }

        //Sets this to not be destroyed when reloading scene
        DontDestroyOnLoad(gameObject);

    }


    public void AgentReachedDoor(VehicleBehaviour agent, GameObject door)
    {
        Debug.Log("Agent reached a door: " + agent.name);
        if (agent.role == AgentRole.Traveller)
        {
            Vector2 spawnPosition;
            while (!TryGetAvailableRandomSpawnPosition(VehicleBehaviour.radius, out spawnPosition));
            var rotation = Quaternion.Euler(0, 0, Random.Range(-180f, 180f));
            agent.transform.SetPositionAndRotation(spawnPosition, rotation);
            agent.target = Random.Range(0, 2) == 0 ? doorLeftTop.position : doorLeftBottom.position;
        }
    }


    //Initializes the game for each level.
    void Start()
    {
        CreateObstacles();
        SpawnTravellingAgents();
        SpawnWanderingAgents();
    }

    private void CreateObstacles()
    {
        for (int i=0; i<numberOfObstacles; i++)
        {
            var obstacleRadius = 3.0f;
            Vector2 obstacleCenter;
            // Find somewhere to place the obstacle.
            while (!TryGetAvailableRandomSpawnPosition(obstacleRadius, out obstacleCenter)) ;
            
            var obstacle = Instantiate<ObstacleBehaviour>(obstaclePrefab, obstacleCenter, Quaternion.identity, transform);
            obstacle.numberOfVertices = 5;
            obstacle.radius = obstacleRadius;
        }
    }

    private bool TryGetAvailableRandomSpawnPosition(float objectRadius, out Vector2 spawnPosition, int maxAttempts = 10, float minDistanceBetweenObjects=1.0f)
    {

        // Check that there are no other objects colliding with this one.
        var colliders = new List<Collider2D>(GetComponentsInChildren<Collider2D>());
        var go = new GameObject();
        var coll = go.AddComponent<CircleCollider2D>();
        coll.radius = objectRadius;

        var found = false;
        for (int attempt = 0; attempt < maxAttempts && !found; attempt++)
        {
            coll.offset = new Vector2(
                Random.Range(xMin + objectRadius, xMax - objectRadius),
                Random.Range(yMin + objectRadius, yMax - objectRadius)
            );

            found = colliders.TrueForAll((other) => coll.Distance(other).distance < minDistanceBetweenObjects);
            //found = true;
            //foreach (var col in colliders)
            //{
            //    // check if the colliders have enough space between them.
            //    if (coll.Distance(col).distance < minDistanceBetweenObjects)
            //    {
            //        found = false;
            //        break;
            //    }
            //}
        }
        spawnPosition = coll.offset;
        if (!found) {
            Debug.Log("Unable to find a placement option after " + maxAttempts + " attempts.");
        }
        Destroy(go);
        return found;
    }

    private void SpawnTravellingAgents()
    {
        for (int i = 0; i < numberOfTravellingAgents; i++)
        {
            Vector2 spawnPosition = Vector2.zero;
            var newTraveller = Instantiate<VehicleBehaviour>(travellerPrefab, spawnPosition, Quaternion.identity, this.transform);
            while (!TryGetAvailableRandomSpawnPosition(VehicleBehaviour.radius, out spawnPosition));

            int choice = Random.Range(0, 2);
            newTraveller.target = choice == 0 ? doorLeftTop.position : doorLeftBottom.position;
            newTraveller.role = AgentRole.Traveller;
            Debug.Log("Spawning a new Agent. " + "Role: " + newTraveller.role + " target: " + newTraveller.target);
        }
    }    

    private void SpawnWanderingAgents()
    {
        // TODO
    }
        
    //Update is called every frame.
    void Update()
    {

    }
    
}
