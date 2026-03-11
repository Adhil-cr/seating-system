document.addEventListener("DOMContentLoaded", async function () {

    const examId = 1;

    const response = await fetch(`/api/seating/view/?exam_id=${examId}`);
    const data = await response.json();

    console.log("Seating data:", data);

});
