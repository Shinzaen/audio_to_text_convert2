// 파일이 선택될 때 호출되는 함수를 정의합니다.
function updateFileName() {
    const fileInput = document.getElementById('audioFile');
    const selectedFileName = document.getElementById('selectedFileName');
    selectedFileName.textContent = fileInput.files[0] ? fileInput.files[0].name : '';
}

// 변환 버튼 클릭 시 호출되는 함수
async function convertAudio() {
    const fileInput = document.getElementById('audioFile');
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    try {
        // 서버에 Ajax 요청을 보냅니다.
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error('Error:', response.status, errorText);
            return;
        }

        // 서버에서 받아온 데이터를 JSON 형식으로 파싱합니다.
        const data = await response.json();

        // 텍스트를 업데이트하는 함수를 호출합니다.
        updateConvertedText(data.transcripts);
    } catch (error) {
        console.error('Error:', error);
    }
}

// 텍스트를 업데이트하는 함수를 정의합니다.
function updateConvertedText(transcripts) {
    const convertedText = document.getElementById('convertedText');
    convertedText.value = transcripts[0] || 'No transcripts available'; // 여러 결과가 있을 경우 첫 번째 결과를 표시
}
