import {useState} from 'react';
import { RotatingLines } from 'react-loader-spinner';

interface Props {
    buttonText: string;
    loadingText: string;
    service: () => Promise<string>;
}

export const ButtonSpinner: React.FC<Props> = ({buttonText, loadingText, service}) => {
    const [data, setData] = useState({
        loading: false,
        statusText: ""
    });

    const onClick = () => {
        setData({loading: true, statusText: loadingText});
        const response = service()

        response.then((responseMessage) => {
            setData({loading: false, statusText: responseMessage});
        }).catch((error) => {
            setData({loading: false, statusText: error.message});
        });
    };


    return (<div style={{padding: '20px'}}>
        <div style={{padding: '10px'}}><button onClick={onClick}>{buttonText}</button></div>
        <div>{data.loading && <RotatingLines visible={true} width='50px'/>}</div>
        <p style={{whiteSpace: 'pre-wrap', width: '500px', margin: 'auto'}}>{data.statusText}</p>
    </div>);
};
