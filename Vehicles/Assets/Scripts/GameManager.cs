﻿using System.Collections;
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
    [Range(1, 10)]
    public int numberOfSocialAgents = 1;
    [Range(1, 5)]
    public float ObstaclesAverageRadius = 3.0f;
    public IList<VehicleBehaviour> vehicles = new List<VehicleBehaviour>();

    //public VehicleBehaviour vehiclePrefab;
    public ObstacleBehaviour obstaclePrefab;
    public TravellerBehaviour travellerPrefab;
    public WandererBehaviour wandererPrefab;
    public SocialBehaviour socialPrefab;

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

        CreateObstacles();

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
        SpawnTravellingAgents();
        SpawnWanderingAgents();
        SpawnSocialAgents();
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
                    //Debug.Log("Unable to palce an obstacle of radius " + obstacleRadius);
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

    public Vector2 GetUnobstructedRegionForAgent()
    {
        if (availableSpots == null)
        {
            PrecomputeObstructedRegions();
            Debug.Log("Availalable spots:" + availableSpots.Count);
        }
        var randomSpot = availableSpots[Random.Range(0, availableSpots.Count)];
        //var x = randomSpot.Item1 * gridCellLengthUnits + xMin;
        //var y = randomSpot.Item2 * gridCellLengthUnits + yMin;
        var x = randomSpot.Item1;
        var y = randomSpot.Item2;
        return new Vector2(x, y);
    }




    private void SpawnTravellingAgents()
    {
        for (int i = 0; i < numberOfTravellingAgents; i++)
        {
            Vector2 spawnPosition = doorRight.position;
            var newTraveller = Instantiate<TravellerBehaviour>(travellerPrefab, spawnPosition, Quaternion.identity, this.transform);
            int choice = Random.Range(0, 2);
            newTraveller.target = choice == 0 ? doorLeftTop.position : doorLeftBottom.position;
            newTraveller.name = "Traveller" + i;
            vehicles.Add(newTraveller);
        }
    }

    private void SpawnWanderingAgents()
    {
        for (int i = 0; i < numberOfWanderingAgents; i++)
        {
            Vector2 spawnPosition = GetUnobstructedRegionForAgent();
            var newWanderer = Instantiate<VehicleBehaviour>(wandererPrefab, spawnPosition, Quaternion.identity, this.transform);

            newWanderer.name = "Wanderer" + i;
            vehicles.Add(newWanderer);
        }
    }

    private void SpawnSocialAgents()
    {
        for (int i = 0; i < numberOfSocialAgents; i++)
        {
            Vector2 spawnPosition = GetUnobstructedRegionForAgent();
            var newSocial = Instantiate<VehicleBehaviour>(socialPrefab, spawnPosition, Quaternion.identity, this.transform);
            newSocial.name = "Social" + i;
            vehicles.Add(newSocial);
        }
    }


    //private bool[,] obstructionGrid;
    private List<System.Tuple<float, float>> availableSpots;
    private const float gridCellLengthUnits = 0.25f;
    private const float minDistanceToAnyObject = 0.5f;
    private void PrecomputeObstructedRegions()
    {
        var colliders = GetComponentsInChildren<Collider2D>().Where(c => c.CompareTag("Wall") || c.CompareTag("Obstacle"));
        Debug.Log("Colliders:" + colliders?.Count());

        // create a CircleCollider used to check if a given position is free.
        var dummy = new GameObject();
        var coll = dummy.AddComponent<CircleCollider2D>();
        coll.radius = VehicleBehaviour.radius;

        // take the colliders for the obstacles and walls.
        //int n = Mathf.CeilToInt((xMax - xMin) / gridCellLengthUnits);
        //int m = Mathf.CeilToInt((yMax - yMin) / gridCellLengthUnits);
        //obstructionGrid = new bool[n, m];
        availableSpots = null;
        availableSpots = new List<System.Tuple<float, float>>();

        int i = 0, j = 0;
        bool spotIsFree;
        for (float x = xMin; x < xMax; x += gridCellLengthUnits, i++)
        {
            for (float y = yMin; y < yMax; y += gridCellLengthUnits, j++)
            {
                coll.offset = new Vector2(x, y);
                spotIsFree = colliders.All(c =>
                {
                    var d = coll.Distance(c);
                    return !d.isOverlapped && d.distance > minDistanceToAnyObject;
                });
                //obstructionGrid[i, j] = spotIsFree;
                if (spotIsFree)
                {
                    availableSpots.Add(System.Tuple.Create(x, y));
                    //Debug.Log("Free spot at (x: " + x + ", y: " + y + ").");
                }
                else
                {
                    //Debug.Log("Obstruction at (x: " + x + ", y: " + y + ").");
                }
            }
        }
        Destroy(dummy, 1.0f);
    }

    public bool TryGetAvailableRandomSpawnPosition(float objectRadius, out Vector2 spawnPosition, int maxAttempts = 10, float minDistanceBetweenObjects = 1.0f)
    {
        var colliders = obstacles.Select(o => o.GetComponent<Collider2D>()).ToList();
        var go = new GameObject("Temp");
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


}
