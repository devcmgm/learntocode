import React from "react";
import taskdata from "./data.json";

interface task {
  id: number;
  type: string;
  description: string;
  status: string;
  assignedPerson: string;
}

export default function Tasks() {
  const tasks = taskdata.map((task: task) => {
    return (
      <li>
        {task.type},{task.description}
      </li>
    );
  });
  return <div>{tasks}</div>;
}
