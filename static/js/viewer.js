
const seatingGrid = document.getElementById("seatingGrid");

students.forEach(student => {

const seat = document.createElement("div");

seat.classList.add("seat");

const colorClass = getSubjectColor(student.subject);

seat.classList.add(colorClass);

seat.innerHTML = `
${student.regNo}
<span>${student.subject}</span>
`;

seatingGrid.appendChild(seat);

});

const subjectColors = {};

function getSubjectColor(subject) {

    if (!subjectColors[subject]) {

        const colors = [
            "#93c5fd",
            "#fde68a",
            "#bbf7d0",
            "#fca5a5",
            "#c4b5fd",
            "#fcd34d",
            "#a7f3d0"
        ];

        const index = Object.keys(subjectColors).length % colors.length;
        subjectColors[subject] = colors[index];

    }

    return subjectColors[subject];
}