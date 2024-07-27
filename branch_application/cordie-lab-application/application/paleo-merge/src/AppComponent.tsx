import React, {useState} from 'react';
import './App.css';
import {FileChooser} from "./FileChooser";
import { import_data, open_pandas_gui, predict_bin_interval, predict_skeletal_material, save_data, save_data_as, update_and_merge_data, update_data } from './services/Services';
import { RotatingLines } from 'react-loader-spinner';
import { ButtonSpinner } from './ButtonSpinner';

export const AppComponent: React.FC = () => {
  // const [path, setPath] = useState<Props>({path: ""});
  // const [rotatingLines, setRotatingLines] = useState<Props>({rotatingLines: false});

  const [data, setData] = useState({
    path: "",
    importSpinner: false,
    importStatusText: "",
    updateSpinner: false,
    updateStatusText: "",
    predictSkeletalMaterialSpinner: false,
    predictSkeletalMaterialStatusText: "",
    predictBinIntervalSpinner: false,
    predictBinIntervalStatusText: ""
  });

  const onChosen = (file: File) => {
    const response = import_data(file.path);
    setData({...data, path: file.path, importSpinner: true, importStatusText: "Importing Data..."});

    response.then((responseMessage) => {  
      setData(({...data, importSpinner: false, importStatusText: responseMessage}));
    })
    .catch((error) => {
      setData(({...data, importSpinner: false, importStatusText: error.message}));
    }); 
  }; 

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
      <ButtonSpinner buttonText="Update Data" loadingText="Updating Data..." service={update_and_merge_data}/>
      <ButtonSpinner buttonText='Predict Skeletal Material' loadingText='Predicting Skeletal Material...' service={predict_skeletal_material}/>
      <ButtonSpinner buttonText='Predict Bin Interval' loadingText='Predicting Bin Interval...' service={predict_bin_interval}/>
      <button onClick={open_pandas_gui}>Open Pandas Gui</button>
      <p></p>
      <button onClick={save_data}>Save</button>
      <button onClick={saveDataAs}>Save As</button>
    </div>
  );
}