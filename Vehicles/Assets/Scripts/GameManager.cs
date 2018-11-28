using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class GameManager : MonoBehaviour
{
    //Static instance of GameManager which allows it to be accessed by any other script.
    public static GameManager instance = null;
    [Range(2, 10)]
    public static int numberOfObstacles = 2;
    [Range(1, 10)]
    public static int numberOfWanderingAgents = 1;
    [Range(1, 10)]
    public static int numberOfTravellingAgents = 1;

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

        InitGame();
    }

    //Initializes the game for each level.
    void InitGame()
    {
        CreateObstacles();
        SpawnTravellingAgents();
        SpawnWanderingAgents();
    }

    private void CreateObstacles()
    {

    }

    private void SpawnTravellingAgents()
    {
        // TODO
    }

    private void SpawnWanderingAgents()
    {
        // TODO

    }

    private void CreateObstacle(Vector2 center, int numberOfVertices)
    {

    }

    //Update is called every frame.
    void Update()
    {

    }
}