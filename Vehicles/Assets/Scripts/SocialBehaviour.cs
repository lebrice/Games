using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;

public class SocialBehaviour : VehicleBehaviour {

    public List<SocialBehaviour> socialGroup;
    public const float joinGroupDistanceThreshold = 2.0f;
    public const float keepWanderingCoolingOffTime = 10.0f;
    public bool readyToJoinGroup;
    // Use this for initialization
    protected override void Start()
    {
        role = AgentRole.Social;
        state = VehicleState.WANDERING;
        previousState = VehicleState.WANDERING;
        SetColor(Color.yellow);
        base.Start();
        StartCoroutine(Social());
    }

    IEnumerator Social()
    {
        while (true)
        {
            SetColor(Color.yellow);
            SelectRandomTarget();
            state = VehicleState.WANDERING;
            SelectRandomTarget();
            readyToJoinGroup = true;
            yield return new WaitUntil(() => OtherSocialAgentNearby(out socialGroup));

            //Debug.Log($"{name} joined a conversation.");
            state = VehicleState.CONVERSATION;
            boxCollider.enabled = false;
            float stayInConversationDuration = Random.Range(0.5f, 2.0f);
            yield return new WaitForSeconds(stayInConversationDuration);

            //Debug.Log($"{name} Left a conversation.");
            readyToJoinGroup = false;
            LeaveSocialGroup();
            state = VehicleState.WANDERING;
            SelectRandomTarget();
            boxCollider.enabled = true;
            SetColor(Color.green);
            yield return new WaitForSeconds(keepWanderingCoolingOffTime);
        }
    }

    protected override void FixedUpdate()
    {
        if(socialGroup == null || socialGroup.Count == 0)
        {
            state = VehicleState.WANDERING;
        }
        
        if (state == VehicleState.WANDERING)
        {
            Wander();
        }
        else if (state == VehicleState.CONVERSATION)
        {
            Conversation();
        }

        base.FixedUpdate();
    }

    private void Conversation()
    {
        Vector2 centroid = GetCentroid(socialGroup);
        Seek(centroid);
    }

    private static Vector3 GetCentroid(List<SocialBehaviour> agents)
    {
        var centroid = Vector3.zero;
        var numAgents = agents.Count;
        foreach (var agent in agents)
        {
            centroid += agent.transform.position;
        }
        return centroid / numAgents;
    }


    private bool OtherSocialAgentNearby(out List<SocialBehaviour> socialGroup)
    {
        var nearbyAgents = AgentsWithinRadius(joinGroupDistanceThreshold,
            (agent) => agent.name != name && agent.role == AgentRole.Social);
        foreach (var vehicle in nearbyAgents)
        {
            //Debug.Log("There is a nearby Social agent:" + vehicle);
            //Debug.Break();
            var agent = vehicle as SocialBehaviour;
            if (!agent.readyToJoinGroup)
            {
                continue;
            }
            socialGroup = agent?.socialGroup;
            if (socialGroup == null)
            {
                socialGroup = new List<SocialBehaviour>();
                socialGroup.Add(this);
                socialGroup.Add(agent);
                agent.socialGroup = socialGroup;

                //Debug.Log($"{name} and {agent.name} are creating a new group.");
            }
            else
            {
                //Debug.Log($"{name} is joining a new group, which currently contains " + socialGroup.Count + " other agents. ");
                socialGroup.Add(this);
            }
            return true;
        }
        socialGroup = null;
        return false;
    }

    private void LeaveSocialGroup()
    {
        socialGroup?.Remove(this);
        if(socialGroup?.Count == 1)
        {
            var lonerInGroup = socialGroup[0];
            //Debug.Log("Destroying the group, since there is only one person left.");
            lonerInGroup.socialGroup = null;
            socialGroup = null;
        }
    }
}
