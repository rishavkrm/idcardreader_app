// src/App.js
import React, { useState } from 'react';
import ReactDOM from 'react-dom';
import { Button, Container, Typography, Box, Grid, AppBar, Toolbar } from '@mui/material';

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [imagePreview, setImagePreview] = useState('');
  const [result, setResult] = useState({});
  // const [processedImage, setProcessedImage] = useState('');
  const [processedImages, setProcessedImages] = useState([]);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const renderedInfo = Object.entries(result).map(([key, value]) => (
    <Box key={key} mt={2}>
      <Typography variant="body1">{key}: {value}</Typography>
    </Box>
  ));
  const handleFileChange = (event) => {
    const file = event.target.files[0];
    setSelectedFile(file);

    const reader = new FileReader();
    reader.onloadend = () => {
      setImagePreview(reader.result);
    };
    reader.readAsDataURL(file);
  };
  const handleUpload = () => {
    if (!selectedFile) {
      alert('Please select a file first.');
      return;
    }

    const formData = new FormData();
    formData.append('file', selectedFile);

    fetch('http://127.0.0.1:8000/upload/', {
      method: 'POST',
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {

        setProcessedImages(data.processed_images);
        // setProcessedImage(data.processed_image);    
        setResult(data.result);
      })
      .catch((error) => {
        console.error('Error:', error);
        setResult('Error occurred while processing.');
      });
  };
  const handleNextImage = () => {
    setCurrentImageIndex((prevIndex) => (prevIndex + 1) % processedImages.length);
  };

  const handlePreviousImage = () => {
    setCurrentImageIndex((prevIndex) =>
      prevIndex === 0 ? processedImages.length - 1 : prevIndex - 1
    );
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
  <AppBar position="static">
    <Toolbar>
      <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
        ID Card Reader
      </Typography>
    </Toolbar>
  </AppBar>
  <Container>
    <Grid
      container
      spacing={2}
      direction="column"
      alignItems="center"
      justifyContent="center"
      style={{ minHeight: 'calc(100vh - 64px)', paddingTop: '20px' }}
    >
      <Grid item container spacing={2} justifyContent="center">
        <Grid item xs={6}>
          {imagePreview && (
            <Box mt={3}>
              <Typography variant="h5">Original Image</Typography>
              <img src={imagePreview} alt="Original" style={{ width: '100%', height: 'auto' }} />
            </Box>
          )}
        </Grid>
        <Grid item xs={6}>
          {processedImages.length > 0 && (
            <Box mt={4}>
              <Typography variant="h5">Gallery</Typography>
              <img
                src={`data:image/png;base64,${processedImages[currentImageIndex]}`}
                alt="Processed"
                style={{ width: '100%', height: 'auto' }}
              />
              <Box mt={2} display="flex" justifyContent="center">
                <Button onClick={handlePreviousImage}>Previous</Button>
                <Button onClick={handleNextImage}>Next</Button>
              </Box>
            </Box>
          )}
        </Grid>
      </Grid>
      <Grid item container justifyContent="center" spacing={2}>
        <Grid item>
          <input
            type="file"
            accept="image/*"
            onChange={handleFileChange}
            style={{ display: 'none' }}
            id="upload-file"
          />
          <label htmlFor="upload-file">
            <Button variant="contained" component="span">
              Upload Image
            </Button>
          </label>
        </Grid>
        <Grid item>
          <Button
            variant="contained"
            onClick={handleUpload} 
            disabled={!selectedFile}
          >
            Send to Server
          </Button>
        </Grid>
      </Grid>
      {result && (
        <Grid item xs={12}>
          <Box mt={4}>
            <Typography variant="body1">{renderedInfo}</Typography>
          </Box>
        </Grid>
      )}
    </Grid>
  </Container>
</Box>

 
  );
}

export default App;

ReactDOM.render(<App />, document.getElementById('root'));
