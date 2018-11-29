using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;

/// <summary>
/// Inspired in part from https://medium.com/@hyperparticle/draw-2d-physics-shapes-in-unity3d-2e0ec634381c
/// </summary>
public class ObstacleBehaviour : MonoBehaviour {
    public int numberOfVertices;
    public float radius;
    public Vector2[] vertices;
    public Material material;
    
    // Use this for initialization
    void Awake()
    {
        Vector2 center = transform.position;
        Debug.Log("Starting ObstacleBehaviour. # of vertices: " + numberOfVertices + " radius: " + radius + " Center: " + center);
    
        vertices = MakeRandomVertices(numberOfVertices, radius);

        // Use the triangulator to get indices for creating triangles
        var triangulator = new Triangulator(vertices);
        var indices = triangulator.Triangulate();

        var vertices3D = System.Array.ConvertAll<Vector2, Vector3>(vertices.ToArray(), v => v);

        // Generate a color for each vertex
        var colors = Enumerable.Range(0, numberOfVertices)
            .Select(i => Color.black)
            .ToArray();

        // Create the mesh
        var mesh = new Mesh()
        {
            vertices = vertices3D,
            triangles = indices,
            colors = colors
        };

        mesh.RecalculateNormals();
        mesh.RecalculateBounds();

        var meshRenderer = gameObject.AddComponent<MeshRenderer>();
        meshRenderer.material = material;

        var filter = gameObject.AddComponent<MeshFilter>();
        filter.mesh = mesh;

        gameObject.AddComponent<ColliderCreator>();
        gameObject.isStatic = true;
    }

    public Vector2[] MakeRandomVertices(int numberOfVertices, float maxRadius)
    {
        var range = Enumerable.Range(0, numberOfVertices);
        var angles = range.Select(i => i * (360 / numberOfVertices)).ToArray();
        var angleVariations = range.Select(i => Random.Range(-(360 / numberOfVertices / 4), (360 / numberOfVertices / 4))).ToArray();
        var lengths = range.Select(i => Random.Range(maxRadius / 4f, maxRadius)).ToArray();
        var vertices = range.Select(i => Vector2.right.Rotate(angles[i] + angleVariations[i]) * lengths[i]).ToArray();
        return vertices.ToArray();
    }

    // Update is called once per frame
    void Update()
    {
    }
}
