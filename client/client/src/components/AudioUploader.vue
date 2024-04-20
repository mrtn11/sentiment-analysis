<template>
  <div>
    <div style="text-align: center;">
      <div class="circle-button-container">
        <div @click="triggerFileInput" class="circle-button">+</div>
        <div class="file-name">{{ fileName }}</div>
        <input type="file" ref="fileInput" @change="handleFileChange" style="display: none;" />
      </div>
      <button class="submit-button" @click="uploadFile" :disabled="isLoading" style>Submit</button>
      <div class="par-or">
        <p>or</p>
      </div>
      <div style=" width: 300px; margin: 0 auto;">
        <div class="search-form" >
          <input type="text" v-model="youtubeLink" class="search-box" placeholder="Paste YouTube link here">
          <button @click="transcribeFromYouTube" class="search-btn">►</button>
        </div>
      </div>
      <div>
        <select v-model="selectedLanguage" id="language-select">
          <option value="en-GB" selected>English</option>
          <option value="sk-SK">Slovak</option>
        </select>
      </div>
      <div v-if="isLoading" class="spinner-container">
        <semipolar-spinner :animation-duration="2000" :size="100" color="#8B0000"/>
      </div>
    </div>

    <br>

    <div v-if="transcription && !isLoading">
      <p>Transcription:</p>
      <p>{{ transcription }}</p><br>
      <p>Overall Sentiment: </p>
      <ul>
        <li>Score {{ overallSentiment.score }}</li>
        <li>Magnitude {{ overallSentiment.magnitude }}</li>
      </ul>

      <br>

      <div style="text-align: center; max-height: 200px;">
      <vue-speedometer :minValue="-1"
        :maxValue="1"
        :value="overallSentiment.score"
        :needleTransitionDuration="2000"
        :segments="3"
        :customSegmentStops="[-1, -0.25, 0, 0.25, 1]"
        :segmentColors='["#D32456", "#FFFFE0", "#FFFFE0", "#90EE90"]'
        needleColor="#2C2C2C"
        textColor="#454545"
        />
      </div>
      <div v-if="sentencesSentiment.length && !isLoading">
        <div class="scale-legend">
          <div class="scale-section" style="background-color: #D32456; color: black;">-1.0 to -0.25</div>
          <div class="scale-section" style="background-color: #FFFFE0; color: black;">-0.25 to 0.25</div>
          <div class="scale-section" style="background-color: #90EE90; color: black;">0.25 to 1.0</div>
        </div>
        <div id="list-demo" class="demo">
          <table>
            <thead>
              <tr>
                <th @click="sortTable('text')">Sentence</th>
                <th @click="sortTable('score')">Score</th>
                <th @click="sortTable('magnitude')">Magnitude</th>
              </tr>
            </thead>
            <transition-group name="list" id="tbody">
              <tr v-for="(sentence, index) in sentencesSentiment" :key="`item-${index}`">
                <td>{{ sentence.text }}</td>
                <td :style="getScoreColor(sentence.score)">{{ sentence.score }}</td>
                <td>{{ sentence.magnitude }}</td>
              </tr>
            </transition-group>
          </table>
        </div>
      </div>
    </div>
  </div>
  <br>
</template>

<script>
import { SemipolarSpinner } from 'epic-spinners';
import VueSpeedometer from "vue-speedometer"

export default {
  components: {
    SemipolarSpinner,
    VueSpeedometer
  },
  data() {
    return {
      selectedFile: null,
      transcription: '',
      overallSentiment: {
         score: 0, 
         magnitude: 0
      },
      sentencesSentiment: [],
      isLoading: false,
      fileName: 'No file selected',
      sortKey: '',
      sortDirection: 'asc',
      youtubeLink: '',
      selectedLanguage: 'en-GB'
    };
  },
  methods: {

    async fetchData() {
      try {
        const response = await fetch('http://104.238.177.32/api/hello');
        const text = await response.text(); 
        console.log(text);
        alert(text); 
      } catch (error) {
        console.error('There was an error!', error);
      }
    },
    
    triggerFileInput() {
      this.$refs.fileInput.click();
    },
    handleFileChange(event) {
      this.selectedFile = event.target.files[0];
      if (this.selectedFile) {
        this.fileName = this.selectedFile.name;
      } else {
        this.fileName = 'No file selected.';
      }
    },
    uploadFile() {
      if (!this.selectedFile) {
        alert("Please select a file first.");
        return;
      }
      this.isLoading = true;
      const formData = new FormData();
      formData.append('file', this.selectedFile);
      formData.append('language', this.selectedLanguage);

      fetch('http://127.0.0.1:5000/transcribe', {
        method: 'POST',
        body: formData,
      })
      .then(response => response.json())
      .then(data => {
        
        this.transcription = data.transcript;
        this.overallSentiment = data.overall_sentiment;
        this.sentencesSentiment = data.sentences_sentiment;
      })
      .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while uploading the file.');
      })
      .finally(() => {
        this.isLoading = false;
      });
    },

    sortTable(key) {
      if (this.sortKey === key) {
        this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
      } else {
        this.sortKey = key;
        this.sortDirection = 'asc';
      }
      
      this.sentencesSentiment.sort((a, b) => {
        let result = 0;
        if (a[key] < b[key]) {
          result = -1;
        } else if (a[key] > b[key]) {
          result = 1;
        }

        return this.sortDirection === 'asc' ? result : -result;
      });
    },
    getScoreColor(score) {
    if (score >= 0.25) {
      return { backgroundColor: '#90EE90', color: 'black' }; 
    }
    if (score > -0.25 && score < 0.25) {
      return { backgroundColor: '#FFFFE0', color: 'black' }; 
    }
    if (score <= -0.25) {
      return { backgroundColor: '#D32456', color: 'black' }; 
    }
  },
  async transcribeFromYouTube() {
      if (!this.validateYouTubeLink(this.youtubeLink)) {
        alert('Please enter a valid YouTube link.');
        return;
      }
      console.log('Transcribing:', this.youtubeLink);

      this.isLoading = true;

      const payload = {
        youtubeLink: this.youtubeLink,
        language: this.selectedLanguage  // Include the selected language
      };

      fetch('http://127.0.0.1:5000/transcribe_youtube', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      })
      .then(response => response.json())
      .then(data => {
        this.transcription = data.transcript;
        this.overallSentiment = data.overall_sentiment;
        this.sentencesSentiment = data.sentences_sentiment;
      })
      .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while processing the YouTube link.');
      })
      .finally(() => {
        this.isLoading = false;
      });

    },
    validateYouTubeLink(link) {
      const pattern = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.?be)\/.+$/;
      return pattern.test(link);
    },
  }
}
</script>

<style scoped>

.circle-button-container {
  display: flex;
  align-items: center;
  gap: 10px; 
  justify-content: center;
}

.circle-button {
  background-color: #8B0000; 
  color: white;
  border: none;
  cursor: pointer;
  font-size: 24px;
  width: 50px; 
  height: 50px;
  border-radius: 50%; 
  text-align: center;
  line-height: 50px; 
  transition: background-color 0.3s; 
  display: flex;
  justify-content: center;
  align-items: center;
}

.circle-button:hover {
  background-color: #A52A2A; 
}

.submit-button {
  background-color: #8B0000; 
  color: white;
  border: none;
  cursor: pointer;
  font-size: 16px; 
  padding: 10px 20px; 
  border-radius: 20px; 
  transition: background-color 0.3s; 
  outline: none; 
  margin-top: 10px;
  font-family: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
}

.submit-button:hover {
  background-color: #A52A2A; 
}

.spinner-container {
  display: flex;
  justify-content: center;
  align-items: center; 
  height: 20vh; 
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  border: none;
  padding: 8px;
  text-align: left;
}

th {
  cursor: pointer;
  background-color: #B3B3B3;
  color:#222222;
}

tr:nth-child(even) {
  background-color: #DCDCDC;
}

.scale-legend {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

.scale-section {
  padding: 10px;
  margin: 0 5px;
  text-align: center;
  width: 150px; 
  border-radius: 5px;
  font-weight: bold;
}

.table-responsive {
  overflow-x: auto; 
}

.styled-table {
  border-collapse: separate; 
  margin: 25px 0;
  font-size: 0.9em;
  min-width: 400px;
  width: 100%;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
  border-radius: 10px; 
  overflow: hidden; 
}

.styled-table thead tr {

  color: #ffffff;
  text-align: left;
}

.styled-table thead tr th:first-child {
  border-top-left-radius: 10px;
}

.styled-table thead tr th:last-child {
  border-top-right-radius: 10px; 
}

.styled-table th,
.styled-table td {
  padding: 12px 15px;
}

.styled-table tbody tr {
  border-bottom: 1px solid #dddddd;
}

.styled-table tbody tr:nth-of-type(even) {
  background-color: #4e4e4e;
}

.styled-table tbody tr:last-of-type td:first-child {
  border-bottom-left-radius: 10px;
}

.styled-table tbody tr:last-of-type td:last-child {
  border-bottom-right-radius: 10px;
}

.styled-table tbody tr:hover {
  background-color: #222222;
  cursor: pointer;
}

.orderupList-enter-active,.orderupList-leave-active{
        transition: all 1s;
}

.orderupList-enter,.orderupList-leave-to{
        opacity: 0;
        transform: translateX(30px);
}

.list-enter-active, .list-leave-active {
  transition: all 1s;
}

.list-enter, .list-leave-to{
  opacity: 0;
  transform: translateX(10px);
}

.list-move {
  transition: transform 1s;
}


.transcribe-btn:hover {
  background-color: #A52A2A;
}

.buttonIn { 
    position: relative; 
    width: 300px;
} 
  
.youtube-input { 
    margin: 0px; 
    padding: 0px; 
    width: 100%; 
    outline: none; 
    height: 30px; 
    border-radius: 30px; 
    font-family: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
} 
  
.transcribe-btn { 
    position: absolute; 
    top: 0; 
    border-radius:8px;
    right: 0px; 
    z-index: 2; 
    border: none; 
    height: 30px; 
    width: 50px;
    cursor: pointer; 
    color: white; 
    background-color: #EF0000; 
    transform: translateX(2px); 
    font-family: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
} 

.par-or{
  padding-top: 5px;
  padding-bottom: 5px;
}

.search-form {
  position: relative; 
}

.search-box {
  width: 100%; 
  padding: 10px 30px 10px 10px; 
  border: 1px solid #ccc; 
  border-radius: 40px; 
  box-sizing: border-box; 
  font-family: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
}

.search-btn:hover {
  background-color: #A52A2A;
}

.search-btn {
  position: absolute; 
  width: 60px;
  height: 60px;
  right: -5px;  
  top: 50%;   
  transform: translateY(-50%); 
  padding: 5px 10px; 
  border: none; 
  background-color: #8B0000; 
  color: white; 
  cursor: pointer; 
  border-radius: 50%; 
  transition: background-color 0.3s;
  font-family: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
}

select {
  margin-top: 10px;
  background-color: white;
  padding: 8px;
  border-radius: 20px; 
  outline: none; 
  cursor: pointer;
  font-family: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
}

option {
  color: black;
}

</style>
