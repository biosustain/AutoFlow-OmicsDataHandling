import React from 'react';
import Graph from "react-graph-vis";


function DesignGraph() {
  const graph = {
    nodes: [
      { id: 1, label: "Intervention", title: "Intervention" },
      { id: 2, label: "Study Design Type", title: "Study Design Type" },
      { id: 3, label: "Observation", title: "Observation" },
     
    ],
    edges: [
      { from: 2, to: 1 },
      { from: 2, to: 3 },
      
    ]
  };
 
  const options = {
    layout: {
      hierarchical: true
    },
    edges: {
      color: "#000000"
    },
    height: "500px"
  };
 
  const events = {
    select: function(event) {
      var { nodes, edges } = event;
    }
  };
  return (
  <div>
      <Graph
      graph={graph}
      options={options}
      events={events}
      getNetwork={network => {
        //  if you want access to vis.js network api you can set the state in a parent component using this property
      }}
    />
  </div>
  );
}

export default DesignGraph;
