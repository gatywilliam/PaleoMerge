async function extractSimpleMessage(response: Promise<{status: number, message: string}>): Promise<string> {
  return response.then((response: {status: number, message: any; }) => {
    if (response.status === 200) {
      return response.message;
    } else {
      throw new Error(response.message);
    }
  })
}

export async function import_data(path: string): Promise<string> {
  const data = await fetch('http://localhost:5000/import?path=' + path);

  return extractSimpleMessage(data.json());
}

export async function update_data(): Promise<any> {
  const data = await fetch('http://localhost:5000/update');
  return data.json();
}

export async function merge_data(): Promise<string> {
  const data = await fetch('http://localhost:5000/merge');
  
  const response = data.json();

  return response.then((response) => {
    const localOverrides = response.message['Local Overrides'];
    const remoteOverrides = response.message['Remote Overrides'];
    let addedColumns = response.message['Added Columns'];
    if (addedColumns.length === 0) {
        addedColumns.push("None");
    }
    // TODO: Remove this line when the backend is fixed
    addedColumns = ["state","order","geogcomments","latlng_basis","record_type","ref_author","ref_pubyr","paleolat","paleomodel","class","genus","late_interval","phylum","cc","paleoage","county","paleolng","latlng_precision","geogscale","family","geoplate","flags","reid_no"];
    // add a space to the end of each column name to test the table
    addedColumns = addedColumns.map((column: string) => " " + column);
    return "Update Successful!\n" + "Local Overrides: " + localOverrides + "\n" + "Remote Overrides: " + remoteOverrides + "\n" + "Added Columns: " + addedColumns;
  })
  .catch((error) => {
    return error.message;
  });
}

export async function save_data() {
  const data = await fetch('http://localhost:5000/save');
  return data.json();
}

export async function save_data_as(path: string) {
  const data = await fetch('http://localhost:5000/save-as?path=' + path);
  return data.json();
}

export async function open_pandas_gui() {
  const data = await fetch('http://localhost:5000/pandas');
  return data.json();
}

export async function update_and_merge_data(): Promise<string> {
  const updateResponse = await update_data();
  if (updateResponse.status !== 200) {
    return extractSimpleMessage(updateResponse);
  } else {
    const mergeResponse = await merge_data();
    return mergeResponse;
  }
}

export async function predict_skeletal_material(): Promise<string> {
  const data = await fetch('http://localhost:5000/predict?column=skeletal_material');
  
  const response = data.json();

  return response.then((response) => {
    const predictions = response.message.skeletal_material.Predictions;
    const copied = response.message.skeletal_material.Copied;
    let lowConfidence = response.message.skeletal_material['Low Confidence'];
    // console.log(lowConfidence);
    // if (Object.keys(lowConfidence).length === 0) {
    //   lowConfidence.push("None");
    // }
    // TODO: Remove this line when the backend is fixed
    // lowConfidence = ["state","order","geogcomments","latlng_basis","record_type","ref_author","ref_pubyr","paleolat","paleomodel","class","genus","late_interval","phylum","cc","paleoage","county","paleolng","latlng_precision","geogscale","family","geoplate","flags","reid_no"];
    // add a space to the end of each column name to test the table
    // lowConfidence = lowConfidence.map((column: string) => " " + column);
    // TODO: Add low confidence columns to the table
    return "Predicted Successful!\n" + "Prediction: " + predictions + "\n" + "Copied: " + copied + "\n" + "Low Confidence: None";
  })
  .catch((error) => {
    return error.message;
  });
}

export async function predict_bin_interval(): Promise<string> {
  const data = await fetch('http://localhost:5000/predict?column=bin_interval');
  
  const response = data.json();

  return response.then((response) => {
    const predictions = response.message.bin_interval.Predictions;
    const copied = response.message.bin_interval.Copied;
    let lowConfidence = response.message.bin_interval['Low Confidence'];
    // if (lowConfidence.length === 0) {
    //   lowConfidence.push("None");
    // }
    // TODO: Remove this line when the backend is fixed
    // lowConfidence = ["state","order","geogcomments","latlng_basis","record_type","ref_author","ref_pubyr","paleolat","paleomodel","class","genus","late_interval","phylum","cc","paleoage","county","paleolng","latlng_precision","geogscale","family","geoplate","flags","reid_no"];
    // add a space to the end of each column name to test the table
    // lowConfidence = lowConfidence.map((column: string) => " " + column);
    // TODO: Add low confidence columns to the table
    return "Predicted Successful!\n" + "Prediction: " + predictions + "\n" + "Copied: " + copied + "\n" + "Low Confidence: None";
  })
  .catch((error) => {
    return error.message;
  });
}
