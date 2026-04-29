// 버튼 클릭 시 실행될 함수 예시
function goToCalendar(userName) {
    // 해당 이름의 페이지로 이동
    window.location.href = '/calendar/' + userName;
}

// 데이터를 서버로 보내는 함수
async function saveData(userName, selectedDates) {
    const response = await fetch('/save_schedule', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: userName, dates: selectedDates })
    });
    
    const result = await response.json();
    if (result.status === 'success') {
        alert('성공적으로 저장되었습니다!');
        window.location.href = '/'; // 메인으로 복귀
    }
}