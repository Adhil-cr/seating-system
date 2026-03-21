document.addEventListener("DOMContentLoaded", function () {
    // SECTION: Department Config
    const DEPT_CONFIG = {
        'Automobile Engineering': { abbr: 'AE', bg: '#CFE3FF', border: '#1E88E5', text: '#0D47A1', label: 'Automobile Engg' },
        'Mechanical Engineering': { abbr: 'ME', bg: '#FFE0B2', border: '#FB8C00', text: '#4E342E', label: 'Mechanical Engg' },
        'Electrical & Electronics Engineering': { abbr: 'EEE', bg: '#E1BEE7', border: '#8E24AA', text: '#4A148C', label: 'Electrical & Electronics' },
        'Computer Engineering': { abbr: 'CT', bg: '#C8E6C9', border: '#2E7D32', text: '#1B5E20', label: 'Computer Engg' },
        'Electronics & Communication': { abbr: 'EC', bg: '#B2EBF2', border: '#00838F', text: '#006064', label: 'Electronics & Comm' },
        'Civil Engineering': { abbr: 'CE', bg: '#F8BBD0', border: '#C2185B', text: '#880E4F', label: 'Civil Engg' },
    };

    const DEPT_FALLBACK = { abbr: '??', bg: '#F5F5F5', border: '#BDBDBD', text: '#424242', label: 'Unknown' };

    function getDept(fullName) {
        if (!fullName) {
            return { ...DEPT_FALLBACK };
        }
        if (DEPT_CONFIG[fullName]) {
            return DEPT_CONFIG[fullName];
        }
        const abbr = fullName
            .split(' ')
            .map(word => word[0])
            .join('')
            .slice(0, 5)
            .toUpperCase();
        return { ...DEPT_FALLBACK, abbr: abbr || DEPT_FALLBACK.abbr, label: fullName };
    }

    // SECTION: State
    let seatData = null;
    let currentExamId = null;
    let currentHallIndex = 0;
    const examsCache = new Map();

    // SECTION: DOM
    const subTitle = document.getElementById("sub-title");
    const statsBar = document.getElementById("stats-bar");
    const toolbar = document.getElementById("toolbar");
    const hallTabs = document.getElementById("hall-tabs");
    const legendBar = document.getElementById("legend-bar");
    const hallTitle = document.getElementById("hall-title");
    const hallDesc = document.getElementById("hall-desc");
    const seatGrid = document.getElementById("seat-grid");
    const examSelect = document.getElementById("exam-select");

    const btnPdf = document.getElementById("btn-pdf");
    const btnExcel = document.getElementById("btn-excel");
    const btnPrint = document.getElementById("btn-print");

    const modalOverlay = document.getElementById("modal-overlay");
    const modalName = document.getElementById("modal-name");
    const modalReg = document.getElementById("modal-reg");
    const modalDetails = document.getElementById("modal-details");
    const modalClose = document.getElementById("modal-close");

    if (!seatGrid || !examSelect) {
        return;
    }

    // SECTION: Helpers
    function padSeatNumber(value) {
        const num = Number(value || 0);
        return String(num).padStart(2, '0');
    }

    function setGridMessage(message) {
        seatGrid.style.gridTemplateColumns = '1fr';
        seatGrid.innerHTML = `<div class="grid-message">${message}</div>`;
    }

    function normalizeSeat(seat, cols) {
        const row = seat.row || seat.Row || 0;
        const col = seat.col || seat.column || seat.Column || 0;
        const seatNumber = seat.seat_number || seat.seatNo || seat.seat || ((row && col && cols) ? ((row - 1) * cols + col) : null);
        const subjects = seat.subjects || seat.subject_codes || seat.subject_code || '';
        return {
            seat_number: seatNumber,
            row: row,
            col: col,
            register_no: seat.register_no || seat.registerNumber || '',
            student_name: seat.student_name || seat.name || '',
            department: seat.department || '',
            semester: seat.semester || seat.sem || seat.semester_no || '',
            subjects: subjects,
            is_multi_subject: Boolean(seat.is_multi_subject) || (String(subjects).includes(','))
        };
    }

    function normalizeHall(hall, defaultName) {
        const cols = hall.cols || hall.columns || hall.col || hall.column || 0;
        const rows = hall.rows || hall.row || 0;
        const seats = Array.isArray(hall.seats) ? hall.seats.map(seat => normalizeSeat(seat, cols)) : [];
        return {
            hall_name: hall.hall_name || hall.name || defaultName || 'Hall',
            room: hall.room || hall.block || '',
            rows: rows,
            cols: cols,
            seats_per_bench: hall.seats_per_bench || hall.seatsPerBench || hall.spb || 1,
            total_seats: hall.total_seats || (rows * cols),
            seats: seats
        };
    }

    function normalizeSeatData(data) {
        if (!data || typeof data !== 'object') {
            return { exam: null, halls: [] };
        }
        if (Array.isArray(data.halls)) {
            const halls = data.halls.map(hall => normalizeHall(hall));
            return { exam: data.exam || null, halls };
        }
        if (data.halls && typeof data.halls === 'object') {
            const halls = Object.keys(data.halls).map(name => normalizeHall(data.halls[name], name));
            return { exam: data.exam || null, halls };
        }
        return { exam: data.exam || null, halls: [] };
    }

    function getExamMeta() {
        const fallback = examsCache.get(String(currentExamId)) || {};
        const exam = (seatData && seatData.exam) ? seatData.exam : fallback;
        return {
            name: exam.name || fallback.name || 'Exam',
            date: exam.date || fallback.date || '—',
            session: exam.session || fallback.session || '',
            subject_codes: Array.isArray(exam.subject_codes) ? exam.subject_codes : []
        };
    }

    // SECTION: Render Stats Bar
    function renderStatsBar(hall, sessionTotalStudents) {
        if (!statsBar) return;
        statsBar.innerHTML = '';

        const totalSeats = hall.total_seats || (hall.rows * hall.cols) || 0;
        const totalStudents = hall.seats.length;

        const sessionPill = document.createElement('div');
        sessionPill.className = 'stat-pill highlight';
        sessionPill.innerHTML = `<strong>${sessionTotalStudents}</strong><span>session students</span>`;
        statsBar.appendChild(sessionPill);

        const totalPill = document.createElement('div');
        totalPill.className = 'stat-pill';
        totalPill.innerHTML = `<strong>${totalSeats}</strong><span>total seats</span>`;
        statsBar.appendChild(totalPill);

        const deptCounts = {};
        hall.seats.forEach(seat => {
            const dept = getDept(seat.department);
            deptCounts[dept.label] = deptCounts[dept.label] || { count: 0, config: dept };
            deptCounts[dept.label].count += 1;
        });

        const sortedDepts = Object.values(deptCounts).sort((a, b) => b.count - a.count);
        sortedDepts.forEach(item => {
            const pill = document.createElement('div');
            pill.className = 'dept-pill';
            pill.style.background = item.config.bg;
            pill.style.border = `0.5px solid ${item.config.border}33`;
            pill.style.color = item.config.text;
            pill.innerHTML = `<span class="dot" style="background:${item.config.border}"></span>${item.count} ${item.config.label}`;
            statsBar.appendChild(pill);
        });

        if (totalStudents === 0) {
            const emptyPill = document.createElement('div');
            emptyPill.className = 'stat-pill';
            emptyPill.innerHTML = `<strong>0</strong><span>students seated</span>`;
            statsBar.appendChild(emptyPill);
        }
    }

    // SECTION: Render Legend
    function renderLegend(hall, examMeta) {
        if (!legendBar) return;
        legendBar.innerHTML = '';

        const deptMap = new Map();
        hall.seats.forEach(seat => {
            const dept = getDept(seat.department);
            deptMap.set(dept.label, dept);
        });

        deptMap.forEach((dept) => {
            const item = document.createElement('div');
            item.className = 'legend-item';
            item.style.color = dept.text;
            const swatch = document.createElement('span');
            swatch.className = 'legend-swatch';
            swatch.style.background = dept.bg;
            swatch.style.borderColor = dept.border;
            item.appendChild(swatch);
            item.appendChild(document.createTextNode(dept.label));
            legendBar.appendChild(item);
        });

        const subjectCodes = (seatData && seatData.exam && Array.isArray(seatData.exam.subject_codes))
            ? seatData.exam.subject_codes
            : (examMeta && examMeta.subject_codes) || [];

        if (subjectCodes.length) {
            const subjectsLine = document.createElement('div');
            subjectsLine.className = 'legend-subjects';
            subjectsLine.textContent = 'Subjects:';
            subjectCodes.forEach(code => {
                const chip = document.createElement('span');
                chip.className = 'subject-chip';
                chip.textContent = code;
                subjectsLine.appendChild(chip);
            });
            legendBar.appendChild(subjectsLine);
        }
    }

    // SECTION: Render Hall Tabs
    function renderHallTabs(halls, activeIndex) {
        hallTabs.innerHTML = '';
        halls.forEach((hall, index) => {
            const tab = document.createElement('button');
            tab.className = `hall-tab${index === activeIndex ? ' active' : ''}`;
            tab.textContent = hall.hall_name;
            tab.addEventListener('click', () => {
                renderAll(index);
            });
            hallTabs.appendChild(tab);
        });
    }

    // SECTION: Render Hall Meta
    function renderHallMeta(hall) {
        if (hallTitle) {
            hallTitle.textContent = `${hall.hall_name} — ${hall.room || ''}`.trim();
        }
        if (hallDesc) {
            const seatsPerBench = hall.seats_per_bench || 1;
            hallDesc.textContent = `${hall.rows} rows · ${hall.cols} columns · ${seatsPerBench} seats/bench · ${hall.total_seats || (hall.rows * hall.cols)} seats`;
        }
    }

    // SECTION: Render Seat Grid
    function renderSeatGrid(hall, examMeta) {
        seatGrid.innerHTML = '';
        seatGrid.style.gridTemplateColumns = `repeat(${hall.cols}, minmax(0, 1fr))`;

        const seatMap = {};
        hall.seats.forEach(seat => {
            seatMap[`${seat.row}-${seat.col}`] = seat;
        });

        for (let r = 1; r <= hall.rows; r += 1) {
            for (let c = 1; c <= hall.cols; c += 1) {
                const seat = seatMap[`${r}-${c}`];
                if (!seat) {
                    const empty = document.createElement('div');
                    empty.className = 'seat-empty';
                    seatGrid.appendChild(empty);
                    continue;
                }

                const dept = getDept(seat.department);
                const subjects = seat.subjects ? String(seat.subjects) : '';
                const subjectList = subjects.split(',').map(s => s.trim()).filter(Boolean);
                const isMulti = seat.is_multi_subject || subjectList.length > 1;
                const multiText = isMulti ? `${subjectList.length} subjects` : '';
                const semesterText = seat.semester ? `Sem ${seat.semester}` : 'Sem —';
                const subjectsText = subjectList.length ? subjectList.join(', ') : '-';

                const card = document.createElement('div');
                card.className = 'seat-card';
                card.style.background = dept.bg;
                card.style.borderLeftColor = dept.border;

                card.innerHTML = `
                    <div class="seat-row">
                        <span class="seat-reg">${seat.register_no}</span>
                        <span class="seat-num">#${padSeatNumber(seat.seat_number)}</span>
                    </div>
                    <div class="seat-name">${seat.student_name}</div>
                    <div class="seat-meta">${semesterText} · <span class="subject-text" style="color:${dept.text}">${subjectsText}</span></div>
                    <div class="seat-footer">
                        <span class="dept-badge" style="background:${dept.border}20;color:${dept.text}">${dept.label}</span>
                        ${isMulti ? `<span class="multi-badge">${multiText}</span>` : ''}
                    </div>
                `;

                card.addEventListener('click', () => {
                    openModal({ ...seat, subjects, subjectList, isMulti }, hall, examMeta);
                });

                seatGrid.appendChild(card);
            }
        }
    }

    // SECTION: Modal
    function openModal(seat, hall, examMeta) {
        if (!modalOverlay) return;
        const dept = getDept(seat.department);
        const subjectsText = seat.subjects || '-';

        modalName.textContent = seat.student_name;
        modalReg.textContent = seat.register_no;

        modalDetails.innerHTML = '';
        const rows = [
            { label: 'Hall', value: `${hall.hall_name} — ${hall.room || ''}`.trim() },
            { label: 'Seat number', value: `#${padSeatNumber(seat.seat_number)}` },
            { label: 'Row / Col', value: `Row ${seat.row}, Col ${seat.col}` },
            { label: 'Semester', value: seat.semester ? `Sem ${seat.semester}` : '—' },
            {
                label: 'Department',
                value: `<span style="background:${dept.bg};color:${dept.text};padding:3px 9px;border-radius:5px;font-size:11px;font-weight:600">${dept.label}</span>`
            },
            {
                label: 'Subject(s)',
                value: `<span class="subject-text" style="color:${dept.text}">${subjectsText}</span>${seat.isMulti ? ' <span style="font-size:10px;color:#E65100"> (arrear)</span>' : ''}`
            },
            { label: 'Exam date', value: `${examMeta.date} · ${examMeta.session}` }
        ];

        rows.forEach((row, index) => {
            const wrapper = document.createElement('div');
            wrapper.className = 'modal-row';
            wrapper.innerHTML = `
                <div class="modal-label">${row.label}</div>
                <div class="modal-value">${row.value}</div>
            `;
            if (index === rows.length - 1) {
                wrapper.style.borderBottom = 'none';
            }
            modalDetails.appendChild(wrapper);
        });

        modalOverlay.style.display = 'flex';
    }

    function closeModal() {
        if (modalOverlay) {
            modalOverlay.style.display = 'none';
        }
    }

    if (modalOverlay) {
        modalOverlay.addEventListener('click', (event) => {
            if (event.target === modalOverlay) {
                closeModal();
            }
        });
    }

    if (modalClose) {
        modalClose.addEventListener('click', closeModal);
    }

    // SECTION: Render All
    function renderAll(hallIndex) {
        if (!seatData || !seatData.halls || seatData.halls.length === 0) {
            setGridMessage('Failed to load seating data. Please try again.');
            return;
        }

        currentHallIndex = hallIndex;
        const hall = seatData.halls[hallIndex];
        const examMeta = getExamMeta();

        if (subTitle) {
            const studentCount = hall.seats.length;
            const roomText = hall.room ? ` — ${hall.room}` : '';
            const seatsPerBench = hall.seats_per_bench || 1;
            subTitle.textContent = `${examMeta.date} · Session: ${examMeta.session} · ${hall.hall_name}${roomText} · ${seatsPerBench} seats/bench · ${studentCount} students`;
        }

        const sessionTotalStudents = seatData.halls.reduce((sum, h) => sum + (h.seats ? h.seats.length : 0), 0);
        renderStatsBar(hall, sessionTotalStudents);
        renderHallTabs(seatData.halls, hallIndex);
        renderLegend(hall, examMeta);
        renderHallMeta(hall);
        renderSeatGrid(hall, examMeta);
    }

    // SECTION: Fetch Seating Data
    async function fetchSeating(examId) {
        currentExamId = examId;
        setGridMessage('Loading...');
        hallTabs.innerHTML = '';
        legendBar.innerHTML = '';
        statsBar.innerHTML = '';

        try {
            const response = await fetch(`/api/seating/view/?exam_id=${examId}`);
            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.error || 'Failed to load seating data.');
            }
            seatData = normalizeSeatData(data);
            renderAll(0);
        } catch (error) {
            seatData = null;
            setGridMessage('Failed to load seating data. Please try again.');
        }
    }

    // SECTION: Load Exams
    async function loadExams() {
        try {
            const response = await fetch('/api/exams/list/');
            const exams = await response.json();
            if (!Array.isArray(exams) || exams.length === 0) {
                examSelect.innerHTML = '<option value="">No exams available</option>';
                setGridMessage('Failed to load seating data. Please try again.');
                return;
            }

            examSelect.innerHTML = '';
            exams.forEach(exam => {
                examsCache.set(String(exam.id), exam);
                const option = document.createElement('option');
                option.value = exam.id;
                option.textContent = exam.name;
                examSelect.appendChild(option);
            });

            const urlExamId = new URLSearchParams(window.location.search).get('exam_id');
            const initialExamId = urlExamId && examsCache.has(String(urlExamId)) ? urlExamId : exams[0].id;
            examSelect.value = initialExamId;
            await fetchSeating(initialExamId);
        } catch (error) {
            examSelect.innerHTML = '<option value="">No exams available</option>';
            setGridMessage('Failed to load seating data. Please try again.');
        }
    }

    // SECTION: Events
    examSelect.addEventListener('change', (event) => {
        fetchSeating(event.target.value);
    });

    if (btnPdf) {
        btnPdf.addEventListener('click', () => {
            if (!currentExamId) return;
            window.location = `/api/seating/export/pdf/?exam_id=${currentExamId}`;
        });
    }

    if (btnExcel) {
        btnExcel.addEventListener('click', () => {
            if (!currentExamId) return;
            window.location = `/api/seating/export/excel/?exam_id=${currentExamId}`;
        });
    }

    if (btnPrint) {
        btnPrint.addEventListener('click', () => {
            window.print();
        });
    }

    // SECTION: Init
    loadExams();
});
