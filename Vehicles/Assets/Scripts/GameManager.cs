using System.Collections;
using System.Collections.Generic;
using System.Linq;
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
    [Range(1, 5)]
    public float ObstaclesAverageRadius = 3.0f;
    public IList<VehicleBehaviour> vehicles = new List<VehicleBehaviour>();

    public VehicleBehaviour vehiclePrefab;
    public ObstacleBehaviour obstaclePrefab;

    public Transform doorLeftTop;
    public Transform doorLeftBottom;
    public Transform doorRight;

    public List<ObstacleBehaviour> obstacles;

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
        if (agent.role == AgentRole.Traveller && door.name != doorRight.name)
        {            
            agent.transform.position = doorRight.transform.position;
            agent.transform.rotation = Quaternion.Euler(new Vector3(0, 0, 180));
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
        obstacles = new List<ObstacleBehaviour>();
        for (int i = 0; i < numberOfObstacles; i++)
        {
            Vector2 obstacleCenter = Vector2.zero;
            // Find somewhere to place the obstacle.
            var obstacleRadius = ObstaclesAverageRadius * Random.Range(0.75f, 1.25f);
            obstaclePrefab.radius = obstacleRadius;
            obstaclePrefab.numberOfVertices = Random.Range(4, 17);
            bool success = false;
            for (int j = 0; j < 5; j++)
            {
                if (!TryGetAvailableRandomSpawnPosition(obstacleRadius, out obstacleCenter, maxAttempts: 20))
                {
                    obstacleRadius /= 2;
                    obstaclePrefab.radius = obstacleRadius;
                    Debug.Log("Unable to palce an obstacle of radius " + obstacleRadius);
                }
                else
                {
                    success = true;
                    break;
                }
            }
            if (!success)
            {
                Debug.LogError("Unable to place an obstacle, even with a radius of " + obstacleRadius +
                    " (Are there perhaps too many objects in the scene?)");
            }

            var obstacle = Instantiate<ObstacleBehaviour>(obstaclePrefab, obstacleCenter, Quaternion.identity, transform);
            obstacles.Add(obstacle);
        }
    }

    public bool TryGetAvailableRandomSpawnPosition(float objectRadius, out Vector2 spawnPosition, int maxAttempts = 10, float minDistanceBetweenObjects = 1.0f)
    {
        var colliders = obstacles.Select(o => o.GetComponent<Collider2D>()).ToList();
        var go = new GameObject();
        var coll = go.AddComponent<CircleCollider2D>();
        coll.radius = objectRadius;
        var found = false;
        for (int attempt = 0; attempt < maxAttempts && !found; attempt++)
        {
            // test out the potential new position.
            coll.offset = new Vector2(
                Random.Range(xMin + objectRadius + minDistanceBetweenObjects, xMax - objectRadius - minDistanceBetweenObjects),
                Random.Range(yMin + objectRadius + minDistanceBetweenObjects, yMax - objectRadius - minDistanceBetweenObjects)
            );

            found = colliders.Count == 0 || colliders.TrueForAll((other) =>
                {
                    var d = coll.Distance(other);
                    //Debug.Log("Attempt " + attempt + "Distance to "+other.name+": " + d.distance + " overlapped: " + d.isOverlapped);
                    return !d.isOverlapped && d.distance > minDistanceBetweenObjects;
                }
            );
        }
        spawnPosition = coll.offset;
        if (!found)
        {
            //Debug.LogWarning("Unable to find a placement location with no overlap. (" + maxAttempts + " attempts)");
        }
        Destroy(go);
        return found;
    }

    private void SpawnTravellingAgents()
    {
        for (int i = 0; i < numberOfTravellingAgents; i++)
        {
            Vector2 spawnPosition = doorRight.position;
            var newTraveller = Instantiate<VehicleBehaviour>(vehiclePrefab, spawnPosition, Quaternion.identity, this.transform);
            int choice = Random.Range(0, 2);
            newTraveller.target = choice == 0 ? doorLeftTop.position : doorLeftBottom.position;
            newTraveller.role = AgentRole.Traveller;
            newTraveller.state = VehicleState.SEEK;
            newTraveller.previousState = VehicleState.SEEK;
            newTraveller.name = "Traveller" + i;
            Debug.Log("Spawning a new Agent. " + "Role: " + newTraveller.role + " target: " + newTraveller.target);
            vehicles.Add(newTraveller);
        }
    }

    private void SpawnWanderingAgents()
    {
        for (int i = 0; i < numberOfWanderingAgents; i++)
        {
            Vector2 spawnPosition;
            if (!TryGetAvailableRandomSpawnPosition(VehicleBehaviour.radius, out spawnPosition, maxAttempts: 20, minDistanceBetweenObjects: 0.1f))
            {
                Debug.LogWarning("Unable able to find a free spot where an agent could be placed! (Are there perhaps too many obstacles ?)");
            }
            var newWanderer = Instantiate<VehicleBehaviour>(vehiclePrefab, spawnPosition, Quaternion.identity, this.transform);

            newWanderer.role = AgentRole.Wanderer;
            newWanderer.state = VehicleState.WANDERING;
            newWanderer.name = "Wanderer" + i;
            Debug.Log("Spawning a new Agent. " + "Role: " + newWanderer.role + " target: " + newWanderer.target);
            vehicles.Add(newWanderer);
        }
    }

    //Update is called every frame.
    void Update()
    {

    }

}
