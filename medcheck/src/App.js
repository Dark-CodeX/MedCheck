import React, { useState } from 'react';
import './App.css';

const BASE_URL = 'http://localhost:10000';

const SendToBackend = async (data, endPoint, content_type) => {
    try {
        const response = await fetch(`${BASE_URL}${endPoint}`, {
            method: 'POST',
            headers: data instanceof FormData ? {} : { 'Content-Type': content_type },
            body: data
        });

        const body = await response.text();
        return { status: response.status, body: body };
    } catch (error) {
        alert('Error sending data to backend: ' + error);
        return { status: 0, body: null };
    }
};


function App() {
    const [inputImage, setInputImage] = useState(null); // preview
    const [fileObj, setFileObj] = useState(null);       // actual file


    const [prediction, setPrediction] = useState('N/A');
    const [confidence, setConfidence] = useState('N/A');
    const [rawScore, setRawScore] = useState('N/A');

    return (
        <div className="App">
            <div className="header">
                <h1>MedCheck</h1>
            </div>
            <div className="main">
                <div className="input">
                    <h2>Input</h2>
                    <img src={inputImage ? inputImage : "/placeholder-image.png"} alt="Input Placeholder" />
                    <input type="file" accept="image/*" onChange={(e) => {
                        const file = e.target.files[0];
                        if (file) {
                            setFileObj(file);

                            const reader = new FileReader();
                            reader.onloadend = () => {
                                setInputImage(reader.result);
                            };
                            reader.readAsDataURL(file);
                        }
                    }} />
                </div>
                <button className="submit-button" onClick={() => {
                    if (inputImage) {
                        const formData = new FormData();
                        formData.append("file", fileObj);

                        SendToBackend(formData, '/predict', null)
                            .then(response => {
                                console.log('Response from backend:', response);
                                if (response.status === 200) {
                                    const data = JSON.parse(response.body);
                                    setPrediction(data.prediction);
                                    setConfidence(data.confidence);
                                    setRawScore(data.raw_score);
                                } else {
                                    alert('Error from backend: ' + response.body);
                                }
                            });
                    } else {
                        alert('Please select an image before submitting.');
                    }
                }}>Predict</button>
                <div className="output">
                    <h2>Output</h2>
                    <label>Prediction: <span className="prediction">{prediction}</span></label>
                    <label>Confidence: <span className="confidence">{confidence !== "N/A" ? confidence * 100 + "%" : confidence}</span></label>
                    <label>Raw Score: <span className="raw-score">{rawScore !== "N/A" ? rawScore * 100 + "%" : rawScore}</span></label>
                </div>
            </div>
        </div>
    );
}

export default App;
