import React, { useState } from 'react';
import { Container, Row, Col, Form, Button } from 'react-bootstrap';
import axios from 'axios';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';
function ImageUploader() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [originalImageUrl, setOriginalImageUrl] = useState(null);
  const [blurredImage, setBlurredImage] = useState(null);

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    setSelectedFile(file);
    setOriginalImageUrl(URL.createObjectURL(file));
  };

  const handleImageUpload = async (event) => {
    event.preventDefault();
    if (selectedFile) {
      const formData = new FormData();
      formData.append('file', selectedFile);

      try {
        const response = await axios.post('http://localhost:5000/blur', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          responseType: 'blob',
        });

        // Create a Blob URL
        const url = URL.createObjectURL(response.data);
        setBlurredImage(url);
      } catch (error) {
        console.error('Error uploading image:', error);
      }
    }
  };

  return (
    <Container>
      <Row className="justify-content-md-center">
        <Col md="auto">
          <h1>Image Blur App</h1>
          <Form onSubmit={handleImageUpload}>
            <input type="file" id="imageUpload" onChange={handleFileChange} />
            <Button variant="primary" type="submit">
              Blur Faces
            </Button>
          </Form>

          {originalImageUrl && (
            <div>
              <h3>Original Image:</h3>
              <img src={originalImageUrl} alt="Original" style={{ maxWidth: '100%' }} />
            </div>
          )}

          {blurredImage && (
            <div>
              <h3>Blurred Image:</h3>
              <img src={blurredImage} alt="Blurred" style={{ maxWidth: '100%' }} />
            </div>
          )}
          
        </Col>
      </Row>
    </Container>
  );
}

export default ImageUploader;
