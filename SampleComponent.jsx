import React, { useState } from "react";
import { predictCreditworthiness, getPredictions } from "./api";

function SampleComponent() {
  const [prediction, setPrediction] = useState(null);

  async function handlePredict() {
    const input = {
      age: 25, education_level: "secondary", farm_size: 2.5, phone_type: "smartphone",
      financial_access: "full", experience_years: 3, extension_access: "yes",
      cooperative_member: "yes", irrigation_access: "yes", dependents: 2, gender: "male"
    };
    const result = await predictCreditworthiness(input);
    setPrediction(result);
  }

  return (
    <div>
      <button onClick={handlePredict}>Predict</button>
      {prediction && (
        <div>
          Creditworthy: {prediction.creditworthy ? "Yes" : "No"}, Probability: {prediction.probability}
        </div>
      )}
    </div>
  );
}