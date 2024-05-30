async function askGPT() {
    const question = document.getElementById('question').value;
    const responseDiv = document.getElementById('answer');
    const video = document.getElementById('loadingVideo');

    video.controls= false;
    video.controller=false;

    // Clear previous answer
    responseDiv.innerHTML = 'Loading...';

    // // Play the video
    // video.play();

    try {
        const response = await fetch('/ask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ question })
        });

        const data = await response.json();

        if (response.ok) {
            const answer = data.answer;
            const audioFile = data.audio_file;
            responseDiv.innerHTML = ''; // Clear the "Loading..." text
            const audio = new Audio(audioFile);
            audio.play();
            displayAnswerOneWordAtATime(answer, responseDiv, video);
        } else {
            responseDiv.innerHTML = `Error: ${data.error}`;
        }
    } catch (error) {
        responseDiv.innerHTML = `Error: ${error.message}`;
        video.pause();
        video.currentTime = 0;  // Reset the video to the start
    }
}

function displayAnswerOneWordAtATime(answer, responseDiv, video) {

    const words = answer;
    let index = 0;
    video.play()
    const interval = setInterval(() => {
        if (index < words.length) {
            responseDiv.innerHTML += words[index];
            index++;
        } else {
            clearInterval(interval);
            video.pause();
            video.currentTime = 0;  // Reset the video to the start

        }
    }, 200); // 0.1 second interval
}
