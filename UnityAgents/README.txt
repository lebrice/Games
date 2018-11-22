What is working:
- The map is created, with the alcoves and the collectibles.
- The portals work for the player and for Enemies (big red pills)
- The agent is not currently able to take the portals, but the Enemies and the player are. (Having trouble with off-mesh links)
- The Enemies do detect whenever they "see" an agent or the player, and write it out to the Console.
- The enemies do choose at random to either despawn, move unobstructed or change direction when they hit the middle obstacle.



What isn't working:
- The perspective is still first-person.
- Agents aren't using any form of AI. The agent present is only trying (and failing) to get to Alcove1.
- There is no HTN (yet).
- The teleport traps aren't yet implemented.

NOTE:
the line of sight of the Enemies is represented with the big red rectangle.
It becomes invisible and the MeshCollider becomes inactive when the Enemy is within the middle wall.


To run: execute AIAgents, if presents, or open the AIAgents folder with Unity to see the SampleScene.