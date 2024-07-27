import React from 'react';

interface Props {
    onChosen: (file: File) => void
}

export const FileChooser: React.FC<Props> = ({onChosen}) => {
    const onChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        if (event.target.files) {
            if (event.target.files.length > 0) {
                onChosen(event.target.files[0]);
            }
        }
    }
    return (<div>
        <input type="file" onChange={onChange}/>
    </div>);
};
