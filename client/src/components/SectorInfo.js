import React, { useEffect, useState } from 'react';
import { Box, Typography, Autocomplete, Select, MenuItem, FormControl, InputLabel, TextField, Card, CardContent } from '@mui/material';
import SectorVisualization from './SectorVisualization'

function SectorInfo() {
  const [sectors, setSectors] = useState([]);
  const [filteredSectors, setFilteredSectors] = useState([]);
  const [selectedSector, setSelectedSector] = useState('');
  const [sectorData, setSectorData] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [sectorDescriptions, setSectorDescriptions] = useState({}); // Store descriptions for each sector
  const [startYear, setStartYear] = useState(2018);
  const [endYear, setEndYear] = useState(2023);

  // Fetch the list of sectors
  useEffect(() => {
    fetch(`${process.env.REACT_APP_API_URL}/api/sector-names`)
      .then((res) => res.json())
      .then((data) => {
        setSectors(data.sectors);
        setFilteredSectors(data.sectors); // Initialize filtered sectors
      });
  }, []);

  // Filter sectors based on the search term
  useEffect(() => {
    setFilteredSectors(
      sectors.filter((sector) =>
        sector.toLowerCase().includes(searchTerm.toLowerCase())
      )
    );
  }, [searchTerm, sectors]);

  // Fetch the description of the selected sector if not already fetched
  useEffect(() => {
    if (selectedSector && !sectorDescriptions[selectedSector]) {
      const encodedSector = encodeURIComponent(selectedSector);
      fetch(`${process.env.REACT_APP_API_URL}/api/sector-description?sector=${encodedSector}`)
        .then((res) => res.json())
        .then((data) => {
          setSectorDescriptions((prev) => ({
            ...prev,
            [selectedSector]: data.description, // Add the description to the state
          }));
        });
    }
  }, [selectedSector, sectorDescriptions]);

  return (
    <Box 
    sx={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}
  
    >
    <Typography variant="h4" gutterBottom >
      Market Sector Information
    </Typography>
    
    <Box sx={{
      display: 'flex',
      flexWrap: 'wrap',
      gap: '1.5rem',
      justifyContent: 'center',
      alignItems: 'center',
      marginBottom: '2rem',
      padding: '1rem',
      borderRadius: '8px',
      backgroundColor: '#f9f9f9', // light gray background for visual grouping
    }}
>

    {/* Autocomplete for searching and selecting a sector */}
    <Autocomplete
      options={sectors}
      getOptionLabel={(option) => option}
      value={selectedSector || null}
      onChange={(event, newValue) => setSelectedSector(newValue || '')}
      isOptionEqualToValue={(option, value) => option === value}
      renderInput={(params) => (
        <TextField {...params} label="Search or Select a Sector" variant="outlined" />
      )}
      sx={{ width: '250px' }}
      // sx={{ marginBottom: '2rem', width: '20rem',  margin: '0 auto'}}
    />

      <FormControl sx={{ minWidth: 120 }}>
        <InputLabel id="start-year-label">Start Year</InputLabel>
        <Select
          labelId="start-year-label"
          value={startYear}
          label="Start Year"
          onChange={(e) => setStartYear(e.target.value)}
        >
          {[...Array(10)].map((_, i) => {
            const year = 2015 + i;
            return <MenuItem key={year} value={year}>{year}</MenuItem>;
          })}
        </Select>
      </FormControl>

      <FormControl sx={{ minWidth: 120 }}>
        <InputLabel id="end-year-label">End Year</InputLabel>
        <Select
          labelId="end-year-label"
          value={endYear}
          label="End Year"
          onChange={(e) => setEndYear(e.target.value)}
        >
          {[...Array(10)].map((_, i) => {
            const year = 2015 + i;
            return <MenuItem key={year} value={year}>{year}</MenuItem>;
          })}
        </Select>
      </FormControl>
    </Box>


    {/* Display the selected sector's description */}
    {selectedSector && (
        <Card sx={{ marginBottom: '2rem' }}>
          <CardContent>
            <Typography variant="h5" gutterBottom>
              {selectedSector} Sector
            </Typography>
            <Typography variant="body1">
              {sectorDescriptions[selectedSector] || 'Loading description...'}
            </Typography>
          </CardContent>
        </Card>
      )}
    {/* {selectedSector && !sectorData && (
      <Typography variant="body1">Loading description for {selectedSector}...</Typography>
    )}
    {sectorData && (
      <Card>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            {sectorData.name}
          </Typography>
          <Typography variant="body1">{sectorData.description}</Typography>
        </CardContent>
      </Card>
    )} */}

    {selectedSector && (
        <SectorVisualization sector={selectedSector} startYear={startYear} endYear={endYear} />
      )}
  </Box>
  );
}

export default SectorInfo;
