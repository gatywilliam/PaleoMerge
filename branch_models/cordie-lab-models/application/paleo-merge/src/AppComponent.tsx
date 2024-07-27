import React, {useState} from 'react';
import './App.css';
import {FileChooser} from "./FileChooser";
import { import_data, save_data, save_data_as, update_data } from './services/Services';
import { RotatingLines } from 'react-loader-spinner';

export const AppComponent: React.FC = () => {
  // const [path, setPath] = useState<Props>({path: ""});
  // const [rotatingLines, setRotatingLines] = useState<Props>({rotatingLines: false});

  const [data, setData] = useState({
    path: "",
    importSpinner: false,
    importStatusText: "",
    updateSpinner: false,
    updateStatusText: ""
  });

  const onChosen = (file: File) => {
    const response = import_data(file.path);
    setData({...data, path: file.path, importSpinner: true, importStatusText: "Importing Data..."});

    response.then((importedData) => {
      if (importedData === undefined || importedData === null) {
        throw new Error("Data is undefined or null.");
      } else if (importedData.length === 0) {
        throw new Error("Data is empty.");
      } else if (importedData.status !== 200) {
        throw new Error(importedData.message);
      }
      
      console.log(importedData); 
      setData(({...data, importSpinner: false, importStatusText: "Import Successful!"}));
    })
    .catch((error) => {
      console.log(error);
      setData(({...data, importSpinner: false, importStatusText: "Import Failed!"}));
    }); 

    /* This is all assuming it is coming from a csv, we just wanna store a path.*/
    // // FileReader Object
    // const reader = new FileReader();

    // // Read file as string
    // reader.readAsText(file);

    // // Load event
    // reader.onload = function (event) {
    //     // Read file data
    //     const csvdata = event.target?.result;

    //     // Split by line break to gets rows Array
    //     let rowData: string[] = [];
    //     if (typeof csvdata === "string") {
    //         rowData = csvdata.split('\n');
    //     }

    //     // Loop on the row Array (change row=0 if you also want to read 1st row)
    //     for (let row = 1; row < rowData.length; row++) {
    //         // Split by comma (,) to get column Array
    //         let rowColData = rowData[row].split(',');
    //     }
  };

  const onUpdateData = () => {
    setData({...data, updateStatusText: "Updating Data...", updateSpinner: true});

    const response = update_data();
    
    response.then((updatedData) => {
      if (updatedData === undefined || updatedData === null) {
        throw new Error("Data is undefined or null.");
      } else if (updatedData.length === 0) {
        throw new Error("Data is empty.");
      } else if (updatedData.status !== 200) {
        throw new Error(updatedData.message);
      }
      
      console.log(updatedData); 
      setData({...data, updateStatusText: "Update Successful!", updateSpinner: false});
    })
    .catch((error) => {
      console.log(error);
      setData({...data, updateStatusText: "Update Failed!", updateSpinner: false});
    })
  }  

  const saveDataAs = () => {
    // Bring up a file chooser to save the data as a xlsx file.
    let input = document.createElement('input');
    input.type = 'file';
    input.onchange = () => {
      // get the path of the file
      try {
        let path = input.files![0].path;
        save_data_as(path);
      } catch (error) {
        console.log("Closed file chooser without selecting a file.");
      }
    };
    input.click();
  }

  return (
    <div className="App">
      <FileChooser onChosen={onChosen}/>
      <RotatingLines visible={data.importSpinner} width='50px'/>
      <p>{data.importStatusText}</p>
      <button onClick={onUpdateData}>Update Data</button>
      <p></p>
      <RotatingLines visible={data.updateSpinner} width='50px'/>
      <p>{data.updateStatusText}</p>
      <button onClick={save_data}>Save</button>
      <button onClick={saveDataAs}>Save As</button>
    </div>
  );
}