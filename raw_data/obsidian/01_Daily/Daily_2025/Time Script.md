
```dataviewjs  
const startDateRange = new Date("2025-04-18");
const endDateRange = new Date("9999-12-31");

const targetFolder = "01_Daily/Daily";
const tasks = [];

function parseTimeRangeAndTitle(line) {
  const match = line.match(/(\d{2}:\d{2})\s*[-–~]\s*(\d{2}:\d{2})\s*(.*)/);
  if (match) return {
    start: match[1],
    end: match[2],
    title: match[3].trim().replace(/^[-•*]+/, "").trim()
  };
  return null;
}

function formatMinutesToHHMM(totalMinutes) {
  const hours = Math.floor(totalMinutes / 60);
  const minutes = totalMinutes % 60;
  return `${hours.toString().padStart(2, "0")}:${minutes.toString().padStart(2, "0")}`;
}

async function processPages() {
  for (const page of dv.pages(`"${targetFolder}"`)) {
    const noteDate = new Date(page.file.ctime);
    if (noteDate < startDateRange || noteDate > endDateRange) continue;

    const fileContent = await dv.io.load(page.file.path);
    const lines = fileContent.split("\n");

    let inDayPlanner = false;

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];

      // Check if entering "Day planner" section
      if (/^#{2,}\s*Day planner\s*$/i.test(line)) {
        inDayPlanner = true;
        continue;
      }

      // If another header of same or higher level appears, exit Day planner section
      if (inDayPlanner && /^#{1,2}\s+/.test(line) && !/^#{2,}\s*Day planner\s*$/i.test(line)) {
        inDayPlanner = false;
      }

      if (inDayPlanner) {
        const info = parseTimeRangeAndTitle(line);
        if (info) {
          try {
            const today = noteDate.toISOString().split("T")[0];
            const startDate = new Date(`${today}T${info.start}:00`);
            const endDate = new Date(`${today}T${info.end}:00`);
            const duration = (endDate - startDate) / (1000 * 60);

            if (duration > 0) {
              tasks.push({ title: info.title, duration });
            }
          } catch (e) {
            dv.span(`❌ Error parsing line: ${line}\n`);
          }
        }
      }
    }
  }

  // Group by task title
  const grouped = tasks.reduce((acc, task) => {
    acc[task.title] = (acc[task.title] || 0) + task.duration;
    return acc;
  }, {});

  // Render
  if (Object.keys(grouped).length > 0) {
    dv.table(["Task", "Total Time (HH:MM)"],
      Object.entries(grouped).map(([title, totalTime]) => [title, formatMinutesToHHMM(totalTime)]));
  } else {
    dv.span("📭 No valid 'Day planner' tasks found in the selected date range.");
  }
}

processPages();


```

```dataviewjs

// 📆 날짜 설정
const targetDate = "2025-04-18";
// const targetDate = dv.current().file.day ? dv.current().file.day.toISODate() : "YYYY-MM-DD";

// 📄 해당 날짜의 파일 가져오기
const filePath = `01_Daily/Daily/${targetDate}.md`;
const page = dv.page(filePath);

if (!page) {
  dv.paragraph(`❌ ${targetDate} 파일을 찾을 수 없습니다.`);
} else {
  // 📝 활동 로그 수집
  const activities = [];
  const fileContent = await dv.io.load(page.file.path);

  // --- 섹션 추출 로직 ---
  const plannerHeader = "## Day planner";
  const headerStartIndex = fileContent.toLowerCase().indexOf(plannerHeader.toLowerCase());
  let sectionContent = "";

  if (headerStartIndex !== -1) {
    const contentAfterHeaderStart = fileContent.substring(headerStartIndex + plannerHeader.length);
    const nextHeaderMatch = contentAfterHeaderStart.match(/^\s*#{2,}\s+/m);
    const contentEndIndex = nextHeaderMatch ? nextHeaderMatch.index : contentAfterHeaderStart.length;
    sectionContent = contentAfterHeaderStart.substring(0, contentEndIndex).trim();
  }
  // --- 섹션 추출 로직 끝 ---

  if (sectionContent) {
    const lines = sectionContent.split('\n');
    const lineRegex = /^\s*[-*]\s+(?:\*\*?)?(\d{2}:\d{2})\s*[-–]\s*(\d{2}:\d{2})(?:\*\*?)?\s*(.*?)(?:\s+#.*)?$/;

    for (const line of lines) {
      if (line.trim().startsWith('#')) continue;

      const match = line.trim().match(lineRegex);
      if (match) {
        const startTimeStr = match[1];
        const endTimeStr = match[2];
        let activityName = match[3].trim();

        // --- 활동 이름 정리 (수정) ---
        // 1) ![[링크]] 또는 [[링크]]를 우선 잡아둔다
        const linkMatch = activityName.match(/!?(\[\[.*?\]\])/);
        const preservedLink = linkMatch ? linkMatch[0] : null; // ← 수정됨

        // 2) 기존 클린업 로직
        activityName = activityName.replace(/^\s*[\p{Emoji_Presentation}\p{Emoji}]\s*/u, '');
        activityName = activityName.replace(/^[ *_~]+|[ *_~]+$/g, '');
        activityName = activityName.replace(/[*_~]{1,3}(.*?)[*_~]{1,3}/g, '$1').trim();


        // 3) 링크가 있었다면, 최종 결과로 덮어쓰기
        if (preservedLink) {
          activityName = preservedLink; // ← 수정됨
        }

        if (!activityName) {
          activityName = "(설명 없음)";
        }
        // --- 활동 이름 정리 끝 ---

        try {
          const start = new Date(`${targetDate}T${startTimeStr}:00`);
          const end = new Date(`${targetDate}T${endTimeStr}:00`);

          if (isNaN(start.getTime()) || isNaN(end.getTime())) {
            console.warn(`유효하지 않은 시간 포맷 건너뜀: ${line.trim()}`);
            continue;
          }
          if (start >= end) {
            console.warn(`종료 시간이 시작 시간보다 빠르거나 같은 항목 건너뜀: ${line.trim()}`);
            continue;
          }

          const duration = (end - start) / (1000 * 60); // 분 단위
          if (duration > 0) {
            activities.push({ activityName, duration });
          }
        } catch (e) {
          console.error(`시간 처리 오류: ${line.trim()}`, e);
          dv.span(`❌ 시간 처리 오류 발생: ${line.trim()}. 개발자 콘솔(Ctrl+Shift+I) 확인`);
        }
      }
    }
  } else {
    dv.paragraph("ℹ️ '## Day planner' 섹션을 찾을 수 없거나 내용이 없습니다.");
  }

  // 🧮 시간 합산
  const grouped = activities.reduce((acc, { activityName, duration }) => {
    acc[activityName] = (acc[activityName] || 0) + duration;
    return acc;
  }, {});

  // 📊 테이블 출력
  if (Object.keys(grouped).length > 0) {
    const formatDuration = (totalMinutes) => {
      if (totalMinutes === 0) return "0m";
      const minutes = Math.round(totalMinutes % 60);
      const hours = Math.floor(totalMinutes / 60);
      let result = "";
      if (hours > 0) result += `${hours}h`;
      if (minutes > 0) {
        if (hours > 0) result += " ";
        result += `${minutes}m`;
      }
      return result;
    };
/*
	for (const [activity, time] of Object.entries(grouped).sort(([, a], [, b]) => b - a)) {
	  dv.paragraph(`${activity} — ${formatDuration(time)}`);
	}
*/
const rows = Object.entries(grouped)
  .sort(([, a], [, b]) => b - a)
  .map(([activity, time]) => `| ${activity} | ${formatDuration(time)} |`);

const header = `| 활동 | 소요 시간 |
|------|-----------|`;

dv.paragraph(header + "\n" + rows.join("\n"));

  } else if (sectionContent) {
    dv.paragraph(`📭 ${targetDate}의 'Day planner' 섹션에서 분석할 활동이 없습니다.`);
  }
}

```

```dataviewjs
// 🗓️ 날짜 범위 설정
const startDate = "2025-04-15"; // 시작 날짜 (YYYY-MM-DD)
const endDate = "2025-04-18";   // 종료 날짜 (YYYY-MM-DD)

// 날짜 범위 생성
function generateDateRange(start, end) {
  const dates = [];
  const currentDate = new Date(start);
  const lastDate = new Date(end);
  
  while (currentDate <= lastDate) {
    dates.push(currentDate.toISOString().split('T')[0]);
    currentDate.setDate(currentDate.getDate() + 1);
  }
  
  return dates;
}

// 시간 포맷 함수
function formatDuration(totalMinutes) {
  if (totalMinutes === 0) return "0m";
  const minutes = Math.round(totalMinutes % 60);
  const hours = Math.floor(totalMinutes / 60);
  let result = "";
  if (hours > 0) result += `${hours}h`;
  if (minutes > 0) {
    if (hours > 0) result += " ";
    result += `${minutes}m`;
  }
  return result;
}

// 날짜 범위 생성
const dateRange = generateDateRange(startDate, endDate);

// 모든 날짜별 활동 데이터를 저장할 객체
const allActivities = {};
const dailyActivities = {};

// 각 날짜별로 활동 데이터 수집
for (const date of dateRange) {
  // 해당 날짜의 파일 가져오기
  const filePath = `01_Daily/Daily/${date}.md`;
  const page = dv.page(filePath);
  
  dailyActivities[date] = {};
  
  if (!page) {
    console.log(`❌ ${date} 파일을 찾을 수 없습니다.`);
    continue;
  }
  
  // 파일 내용 가져오기
  const fileContent = await dv.io.load(page.file.path);
  
  // Day planner 섹션 추출
  const plannerHeader = "## Day planner";
  const headerStartIndex = fileContent.toLowerCase().indexOf(plannerHeader.toLowerCase());
  let sectionContent = "";
  
  if (headerStartIndex !== -1) {
    const contentAfterHeaderStart = fileContent.substring(headerStartIndex + plannerHeader.length);
    const nextHeaderMatch = contentAfterHeaderStart.match(/^\s*#{2,}\s+/m);
    const contentEndIndex = nextHeaderMatch ? nextHeaderMatch.index : contentAfterHeaderStart.length;
    sectionContent = contentAfterHeaderStart.substring(0, contentEndIndex).trim();
  }
  
  if (sectionContent) {
    const lines = sectionContent.split('\n');
    const lineRegex = /^\s*[-*]\s+(?:\*\*?)?(\d{2}:\d{2})\s*[-–]\s*(\d{2}:\d{2})(?:\*\*?)?\s*(.*?)(?:\s+#.*)?$/;
    
    for (const line of lines) {
      if (line.trim().startsWith('#')) continue;
      
      const match = line.trim().match(lineRegex);
      if (match) {
        const startTimeStr = match[1];
        const endTimeStr = match[2];
        let activityName = match[3].trim();
        
        // 활동 이름 정리 (수정)
        const linkMatch = activityName.match(/!?(\[\[.*?\]\])/);
        const preservedLink = linkMatch ? linkMatch[0] : null;
        
        activityName = activityName.replace(/^\s*[\p{Emoji_Presentation}\p{Emoji}]\s*/u, '');
        activityName = activityName.replace(/^[ *_~]+|[ *_~]+$/g, '');
        activityName = activityName.replace(/[*_~]{1,3}(.*?)[*_~]{1,3}/g, '$1').trim();
        
        if (preservedLink) {
          activityName = preservedLink;
        }
        
        if (!activityName) {
          activityName = "(설명 없음)";
        }
        
        try {
          const start = new Date(`${date}T${startTimeStr}:00`);
          const end = new Date(`${date}T${endTimeStr}:00`);
          
          if (isNaN(start.getTime()) || isNaN(end.getTime())) {
            console.warn(`유효하지 않은 시간 포맷 건너뜀: ${line.trim()}`);
            continue;
          }
          if (start >= end) {
            console.warn(`종료 시간이 시작 시간보다 빠르거나 같은 항목 건너뜀: ${line.trim()}`);
            continue;
          }
          
          const duration = (end - start) / (1000 * 60); // 분 단위
          
          if (duration > 0) {
            // 해당 날짜의 활동 정보 저장
            dailyActivities[date][activityName] = (dailyActivities[date][activityName] || 0) + duration;
            
            // 전체 활동 목록에 추가
            if (!allActivities[activityName]) {
              allActivities[activityName] = {};
            }
            allActivities[activityName][date] = (allActivities[activityName][date] || 0) + duration;
          }
        } catch (e) {
          console.error(`시간 처리 오류: ${line.trim()}`, e);
        }
      }
    }
  }
}

// 모든 활동 목록 가져오기
const allActivityNames = Object.keys(allActivities);

// 테이블 헤더 생성 
let headers = ["활동"];
for (const date of dateRange) {
  // 날짜 포맷 변경 (YYYY-MM-DD -> MM/DD)
  const shortDate = date.substring(5).replace("-", "/");
  headers.push(shortDate);
}
headers.push("합계");

// 테이블 데이터 생성
const tableData = [];

// 각 활동별로 날짜별 시간 및 합계 계산
for (const activity of allActivityNames) {
  const row = [activity];
  let totalMinutes = 0;
  
  for (const date of dateRange) {
    const minutes = allActivities[activity][date] || 0;
    row.push(minutes > 0 ? formatDuration(minutes) : "-");
    totalMinutes += minutes;
  }
  
  row.push(formatDuration(totalMinutes));
  tableData.push(row);
}

// 테이블 데이터 정렬 (합계 시간 기준 내림차순)
tableData.sort((a, b) => {
  const getMinutes = (timeStr) => {
    if (timeStr === "-" || timeStr === "0m") return 0;
    let totalMinutes = 0;
    const hourMatch = timeStr.match(/(\d+)h/);
    const minuteMatch = timeStr.match(/(\d+)m/);
    if (hourMatch) totalMinutes += parseInt(hourMatch[1]) * 60;
    if (minuteMatch) totalMinutes += parseInt(minuteMatch[1]);
    return totalMinutes;
  };
  
  return getMinutes(b[b.length - 1]) - getMinutes(a[a.length - 1]);
});

// 테이블 형식 생성
let table = `| ${headers.join(" | ")} |\n`;
table += `| ${headers.map(_ => "---").join(" | ")} |\n`;

for (const row of tableData) {
  table += `| ${row.join(" | ")} |\n`;
}

// 테이블 출력
dv.paragraph(`### ${startDate} ~ ${endDate} 활동 시간 분석`);
dv.paragraph(table);

```


```dataviewjs
// 🗓️ 날짜 범위 설정
const startDate = "2025-04-01"; // 시작 날짜 (YYYY-MM-DD)
const endDate = "2025-04-30";   // 종료 날짜 (YYYY-MM-DD)

// ----- 유틸리티 함수 -----

// 날짜 범위 생성
function generateDateRange(start, end) {
  const dates = [];
  const currentDate = new Date(start);
  const lastDate = new Date(end);
  
  while (currentDate <= lastDate) {
    dates.push(currentDate.toISOString().split('T')[0]);
    currentDate.setDate(currentDate.getDate() + 1);
  }
  
  return dates;
}

// 날짜로부터 주차 정보 계산 (YYYY-WW 형식)
function getWeekNumber(dateStr) {
  const date = new Date(dateStr);
  const firstDayOfYear = new Date(date.getFullYear(), 0, 1);
  const pastDaysOfYear = (date - firstDayOfYear) / 86400000;
  const weekNum = Math.ceil((pastDaysOfYear + firstDayOfYear.getDay() + 1) / 7);
  return `${date.getFullYear()}-W${weekNum.toString().padStart(2, '0')}`;
}

// 주차 표시 형식화 (YYYY-WW -> WW주차)
function formatWeekDisplay(weekKey) {
  const [year, weekNum] = weekKey.split('-W');
  return `${parseInt(weekNum)}주차`;
}

// 시간 포맷 함수
function formatDuration(totalMinutes) {
  if (totalMinutes === 0) return "0m";
  const minutes = Math.round(totalMinutes % 60);
  const hours = Math.floor(totalMinutes / 60);
  let result = "";
  if (hours > 0) result += `${hours}h`;
  if (minutes > 0) {
    if (hours > 0) result += " ";
    result += `${minutes}m`;
  }
  return result;
}

// 문자열 시간을 분으로 변환
function getMinutesFromTimeStr(timeStr) {
  if (timeStr === "-" || timeStr === "0m") return 0;
  let totalMinutes = 0;
  const hourMatch = timeStr.match(/(\d+)h/);
  const minuteMatch = timeStr.match(/(\d+)m/);
  if (hourMatch) totalMinutes += parseInt(hourMatch[1]) * 60;
  if (minuteMatch) totalMinutes += parseInt(minuteMatch[1]);
  return totalMinutes;
}

// ----- 메인 로직 -----

// 날짜 범위 생성
const dateRange = generateDateRange(startDate, endDate);

// 날짜를 주차별로 그룹화
const weekMap = {};
const dateToWeek = {};

for (const date of dateRange) {
  const weekKey = getWeekNumber(date);
  if (!weekMap[weekKey]) {
    weekMap[weekKey] = [];
  }
  weekMap[weekKey].push(date);
  dateToWeek[date] = weekKey;
}

// 주차 목록 (정렬)
const weekKeys = Object.keys(weekMap).sort();

// 데이터 저장 객체
const activityData = {};  // 활동 -> 주차 -> 시간(분)
const weeklyTotals = {};  // 주차 -> 총 시간(분)

// 각 날짜별로 활동 데이터 수집
for (const date of dateRange) {
  // 해당 날짜의 파일 가져오기
  const filePath = `01_Daily/Daily/${date}.md`;
  const page = dv.page(filePath);
  
  if (!page) {
    // console.log(`❌ ${date} 파일을 찾을 수 없습니다.`);
    continue;  // 조용히 넘어감
  }
  
  try {
    // 파일 내용 가져오기
    const fileContent = await dv.io.load(page.file.path);
    
    // Day planner 섹션 추출
    const plannerHeader = "## Day planner";
    const headerStartIndex = fileContent.toLowerCase().indexOf(plannerHeader.toLowerCase());
    
    if (headerStartIndex === -1) continue;  // Day planner 섹션이 없으면 스킵
    
    const contentAfterHeaderStart = fileContent.substring(headerStartIndex + plannerHeader.length);
    const nextHeaderMatch = contentAfterHeaderStart.match(/^\s*#{2,}\s+/m);
    const contentEndIndex = nextHeaderMatch ? nextHeaderMatch.index : contentAfterHeaderStart.length;
    const sectionContent = contentAfterHeaderStart.substring(0, contentEndIndex).trim();
    
    if (!sectionContent) continue;  // 섹션 내용이 없으면 스킵
    
    // 활동 시간 추출
    const lines = sectionContent.split('\n');
    const lineRegex = /^\s*[-*]\s+(?:\*\*?)?(\d{2}:\d{2})\s*[-–]\s*(\d{2}:\d{2})(?:\*\*?)?\s*(.*?)(?:\s+#.*)?$/;
    
    for (const line of lines) {
      if (line.trim().startsWith('#')) continue;
      
      const match = line.trim().match(lineRegex);
      if (!match) continue;
      
      const startTimeStr = match[1];
      const endTimeStr = match[2];
      let activityName = match[3].trim();
      
      // 활동 이름 정리
      const linkMatch = activityName.match(/!?(\[\[.*?\]\])/);
      const preservedLink = linkMatch ? linkMatch[0] : null;
      
      activityName = activityName.replace(/^\s*[\p{Emoji_Presentation}\p{Emoji}]\s*/u, '');
      activityName = activityName.replace(/^[ *_~]+|[ *_~]+$/g, '');
      activityName = activityName.replace(/[*_~]{1,3}(.*?)[*_~]{1,3}/g, '$1').trim();
      
      if (preservedLink) {
        activityName = preservedLink;
      }
      
      if (!activityName) {
        activityName = "(설명 없음)";
      }
      
      try {
        const start = new Date(`${date}T${startTimeStr}:00`);
        const end = new Date(`${date}T${endTimeStr}:00`);
        
        if (isNaN(start.getTime()) || isNaN(end.getTime())) continue;
        if (start >= end) continue;
        
        const duration = (end - start) / (1000 * 60); // 분 단위
        if (duration <= 0) continue;
        
        // 해당 주차
        const weekKey = dateToWeek[date];
        
        // 활동 데이터에 추가
        if (!activityData[activityName]) {
          activityData[activityName] = {};
        }
        if (!activityData[activityName][weekKey]) {
          activityData[activityName][weekKey] = 0;
        }
        activityData[activityName][weekKey] += duration;
        
        // 주차별 총합에 추가
        if (!weeklyTotals[weekKey]) {
          weeklyTotals[weekKey] = 0;
        }
        weeklyTotals[weekKey] += duration;
        
      } catch (e) {
        // console.error(`시간 처리 오류: ${line.trim()}`, e);
        continue;  // 오류 발생 시 조용히 넘어감
      }
    }
  } catch (e) {
    // console.error(`파일 처리 오류: ${filePath}`, e);
    continue;  // 오류 발생 시 조용히 넘어감
  }
}

// ----- 결과 테이블 생성 -----

// 활동 목록 (알파벳 순)
const activityNames = Object.keys(activityData).sort();

// 테이블 헤더 생성
let headers = ["활동"];
for (const weekKey of weekKeys) {
  headers.push(formatWeekDisplay(weekKey));
}
headers.push("합계");

// 테이블 데이터 생성
const tableData = [];
const activityTotals = {};  // 활동별 총합

// 각 활동별로 주차별 시간 및 합계 계산
for (const activity of activityNames) {
  const row = [activity];
  let totalMinutes = 0;
  
  for (const weekKey of weekKeys) {
    const minutes = activityData[activity][weekKey] || 0;
    row.push(minutes > 0 ? formatDuration(minutes) : "-");
    totalMinutes += minutes;
  }
  
  row.push(formatDuration(totalMinutes));
  activityTotals[activity] = totalMinutes;
  tableData.push(row);
}

// 테이블 데이터 정렬 (합계 시간 기준 내림차순)
tableData.sort((a, b) => {
  const activityA = a[0];
  const activityB = b[0];
  return activityTotals[activityB] - activityTotals[activityA];
});

// 주차별 합계 행 추가
const weeklyTotalRow = ["총합"];
let grandTotal = 0;

for (const weekKey of weekKeys) {
  const total = weeklyTotals[weekKey] || 0;
  weeklyTotalRow.push(formatDuration(total));
  grandTotal += total;
}

weeklyTotalRow.push(formatDuration(grandTotal));
tableData.push(weeklyTotalRow);

// 테이블 형식 생성
let table = `| ${headers.join(" | ")} |\n`;
table += `| ${headers.map(_ => "---").join(" | ")} |\n`;

for (let i = 0; i < tableData.length; i++) {
  const row = tableData[i];
  
  // 마지막 행(총합)은 강조 표시
  if (i === tableData.length - 1) {
    table += `| **${row.join("** | **")}** |\n`;
  } else {
    table += `| ${row.join(" | ")} |\n`;
  }
}

// 테이블 출력
dv.paragraph(`### ${startDate} ~ ${endDate} 주차별 활동 시간 분석`);
dv.paragraph(table);
```

---


```dataviewjs
// 🗓️ 날짜 범위 설정
const startDate = "2025-04-15"; // 시작 날짜 (YYYY-MM-DD)
const endDate = "2025-04-18";   // 종료 날짜 (YYYY-MM-DD)

// 날짜 범위 생성
function generateDateRange(start, end) {
  const dates = [];
  const currentDate = new Date(start);
  const lastDate = new Date(end);
  
  while (currentDate <= lastDate) {
    dates.push(currentDate.toISOString().split('T')[0]);
    currentDate.setDate(currentDate.getDate() + 1);
  }
  
  return dates;
}

// 시간 포맷 함수
function formatDuration(totalMinutes) {
  if (totalMinutes === 0) return "0m";
  const minutes = Math.round(totalMinutes % 60);
  const hours = Math.floor(totalMinutes / 60);
  let result = "";
  if (hours > 0) result += `${hours}h`;
  if (minutes > 0) {
    if (hours > 0) result += " ";
    result += `${minutes}m`;
  }
  return result;
}

// 날짜 범위 생성
const dateRange = generateDateRange(startDate, endDate);

// 모든 날짜별 활동 데이터를 저장할 객체
const allActivities = {};
const dailyActivities = {};

// 각 날짜별로 활동 데이터 수집
for (const date of dateRange) {
  // 해당 날짜의 파일 가져오기
  const filePath = `01_Daily/Daily/${date}.md`;
  const page = dv.page(filePath);
  
  dailyActivities[date] = {};
  
  if (!page) {
    console.log(`❌ ${date} 파일을 찾을 수 없습니다.`);
    continue;
  }
  
  // 파일 내용 가져오기
  const fileContent = await dv.io.load(page.file.path);
  
  // Day planner 섹션 추출
  const plannerHeader = "## Day planner";
  const headerStartIndex = fileContent.toLowerCase().indexOf(plannerHeader.toLowerCase());
  let sectionContent = "";
  
  if (headerStartIndex !== -1) {
    const contentAfterHeaderStart = fileContent.substring(headerStartIndex + plannerHeader.length);
    const nextHeaderMatch = contentAfterHeaderStart.match(/^\s*#{2,}\s+/m);
    const contentEndIndex = nextHeaderMatch ? nextHeaderMatch.index : contentAfterHeaderStart.length;
    sectionContent = contentAfterHeaderStart.substring(0, contentEndIndex).trim();
  }
  
  if (sectionContent) {
    const lines = sectionContent.split('\n');
    const lineRegex = /^\s*[-*]\s+(?:\*\*?)?(\d{2}:\d{2})\s*[-–]\s*(\d{2}:\d{2})(?:\*\*?)?\s*(.*?)(?:\s+#.*)?$/;
    
    for (const line of lines) {
      if (line.trim().startsWith('#')) continue;
      
      const match = line.trim().match(lineRegex);
      if (match) {
        const startTimeStr = match[1];
        const endTimeStr = match[2];
        let activityName = match[3].trim();
        
        // 활동 이름 정리 (수정)
        const linkMatch = activityName.match(/!?(\[\[.*?\]\])/);
        const preservedLink = linkMatch ? linkMatch[0] : null;
        
        activityName = activityName.replace(/^\s*[\p{Emoji_Presentation}\p{Emoji}]\s*/u, '');
        activityName = activityName.replace(/^[ *_~]+|[ *_~]+$/g, '');
        activityName = activityName.replace(/[*_~]{1,3}(.*?)[*_~]{1,3}/g, '$1').trim();
        
        if (preservedLink) {
          activityName = preservedLink;
        }
        
        if (!activityName) {
          activityName = "(설명 없음)";
        }
        
        try {
          const start = new Date(`${date}T${startTimeStr}:00`);
          const end = new Date(`${date}T${endTimeStr}:00`);
          
          if (isNaN(start.getTime()) || isNaN(end.getTime())) {
            console.warn(`유효하지 않은 시간 포맷 건너뜀: ${line.trim()}`);
            continue;
          }
          if (start >= end) {
            console.warn(`종료 시간이 시작 시간보다 빠르거나 같은 항목 건너뜀: ${line.trim()}`);
            continue;
          }
          
          const duration = (end - start) / (1000 * 60); // 분 단위
          
          if (duration > 0) {
            // 해당 날짜의 활동 정보 저장
            dailyActivities[date][activityName] = (dailyActivities[date][activityName] || 0) + duration;
            
            // 전체 활동 목록에 추가
            if (!allActivities[activityName]) {
              allActivities[activityName] = {};
            }
            allActivities[activityName][date] = (allActivities[activityName][date] || 0) + duration;
          }
        } catch (e) {
          console.error(`시간 처리 오류: ${line.trim()}`, e);
        }
      }
    }
  }
}

// 모든 활동 목록 가져오기
const allActivityNames = Object.keys(allActivities);

// 테이블 헤더 생성 
let headers = ["활동"];
for (const date of dateRange) {
  // 날짜 포맷 변경 (YYYY-MM-DD -> MM/DD)
  const shortDate = date.substring(5).replace("-", "/");
  headers.push(shortDate);
}
headers.push("합계");

// 테이블 데이터 생성
const tableData = [];

// 각 활동별로 날짜별 시간 및 합계 계산
for (const activity of allActivityNames) {
  const row = [activity];
  let totalMinutes = 0;
  
  for (const date of dateRange) {
    const minutes = allActivities[activity][date] || 0;
    row.push(minutes > 0 ? formatDuration(minutes) : "-");
    totalMinutes += minutes;
  }
  
  row.push(formatDuration(totalMinutes));
  tableData.push(row);
}

// 테이블 데이터 정렬 (합계 시간 기준 내림차순)
tableData.sort((a, b) => {
  const getMinutes = (timeStr) => {
    if (timeStr === "-" || timeStr === "0m") return 0;
    let totalMinutes = 0;
    const hourMatch = timeStr.match(/(\d+)h/);
    const minuteMatch = timeStr.match(/(\d+)m/);
    if (hourMatch) totalMinutes += parseInt(hourMatch[1]) * 60;
    if (minuteMatch) totalMinutes += parseInt(minuteMatch[1]);
    return totalMinutes;
  };
  
  return getMinutes(b[b.length - 1]) - getMinutes(a[a.length - 1]);
});

// 테이블 형식 생성
let table = `| ${headers.join(" | ")} |\n`;
table += `| ${headers.map(_ => "---").join(" | ")} |\n`;

for (const row of tableData) {
  table += `| ${row.join(" | ")} |\n`;
}

// 테이블 출력
dv.paragraph(`### ${startDate} ~ ${endDate} 활동 시간 분석`);
dv.paragraph(table);

// ----------------- 차트 생성 코드 추가 -----------------

// 차트 데이터 생성 함수
function createChartData(activities, dates) {
  // For stacked bar chart (일별 활동 시간)
  const stackedBarData = {
    labels: dates.map(date => date.substring(5).replace("-", "/")), // MM/DD 형식
    datasets: []
  };

  // For pie chart (활동별 총 시간)
  const pieData = {
    labels: [],
    datasets: [{
      data: [],
      backgroundColor: []
    }]
  };

  // For line chart (활동별 시간 추이)
  const lineData = {
    labels: dates.map(date => date.substring(5).replace("-", "/")), // MM/DD 형식
    datasets: []
  };

  // 색상 옵션
  const colors = [
    'rgba(255, 99, 132, 0.7)',
    'rgba(54, 162, 235, 0.7)',
    'rgba(255, 206, 86, 0.7)',
    'rgba(75, 192, 192, 0.7)',
    'rgba(153, 102, 255, 0.7)',
    'rgba(255, 159, 64, 0.7)',
    'rgba(199, 199, 199, 0.7)',
    'rgba(83, 102, 255, 0.7)',
    'rgba(40, 159, 64, 0.7)',
    'rgba(210, 199, 199, 0.7)'
  ];

  let colorIndex = 0;
  
  // 활동별 총 시간 계산 (파이 차트용)
  const activityTotals = {};
  Object.keys(activities).forEach(activity => {
    let total = 0;
    dates.forEach(date => {
      total += activities[activity][date] || 0;
    });
    activityTotals[activity] = total;
  });
  
  // 활동별 데이터셋 생성
  Object.keys(activities).forEach(activity => {
    const color = colors[colorIndex % colors.length];
    colorIndex++;
    
    // 일별 막대 차트용 데이터
    stackedBarData.datasets.push({
      label: activity,
      data: dates.map(date => (activities[activity][date] || 0) / 60), // 시간 단위로 변환
      backgroundColor: color
    });
    
    // 라인 차트용 데이터
    lineData.datasets.push({
      label: activity,
      data: dates.map(date => (activities[activity][date] || 0) / 60), // 시간 단위로 변환
      borderColor: color,
      tension: 0.1
    });
    
    // 파이 차트용 데이터 (총 시간이 0보다 큰 경우만)
    if (activityTotals[activity] > 0) {
      pieData.labels.push(activity);
      pieData.datasets[0].data.push(activityTotals[activity] / 60); // 시간 단위로 변환
      pieData.datasets[0].backgroundColor.push(color);
    }
  });
  
  // 파이 차트 데이터 정렬 (크기 내림차순)
  const indices = Array.from(Array(pieData.labels.length).keys());
  indices.sort((a, b) => pieData.datasets[0].data[b] - pieData.datasets[0].data[a]);
  
  pieData.labels = indices.map(i => pieData.labels[i]);
  pieData.datasets[0].data = indices.map(i => pieData.datasets[0].data[i]);
  pieData.datasets[0].backgroundColor = indices.map(i => pieData.datasets[0].backgroundColor[i]);

  return {
    stackedBar: stackedBarData,
    pie: pieData,
    line: lineData
  };
}

// 옵시디언 차트 코드 생성 함수
function generateChartCode(chartData) {
  // 일별 활동 시간 (스택 막대 차트)
  let stackedBarChartCode = `\`\`\`chart
type: bar
labels: [${chartData.stackedBar.labels.map(l => `"${l}"`).join(', ')}]
series:
${chartData.stackedBar.datasets.map(dataset => 
  `  - title: ${dataset.label}
    data: [${dataset.data.join(', ')}]`
).join('\n')}
stacked: true
tension: 0.2
width: 80%
labelColors: false
fill: false
beginAtZero: true
title: 일별 활동 시간 (시간)
legend: true
\`\`\``;

  // 활동별 총 시간 (파이 차트)
  let pieChartCode = `\`\`\`chart
type: pie
labels: [${chartData.pie.labels.map(l => `"${l}"`).join(', ')}]
series:
  - data: [${chartData.pie.datasets[0].data.join(', ')}]
width: 60%
legendPosition: right
title: 활동별 총 시간 (시간)
\`\`\``;

  // 활동별 시간 추이 (라인 차트)
  let lineChartCode = `\`\`\`chart
type: line
labels: [${chartData.line.labels.map(l => `"${l}"`).join(', ')}]
series:
${chartData.line.datasets.map(dataset => 
  `  - title: ${dataset.label}
    data: [${dataset.data.join(', ')}]`
).join('\n')}
tension: 0.2
width: 80%
labelColors: false
fill: false
beginAtZero: true
title: 일별 활동 시간 추이 (시간)
legend: true
\`\`\``;

  return {
    stackedBar: stackedBarChartCode,
    pie: pieChartCode,
    line: lineChartCode
  };
}

// 차트 데이터 생성
const chartData = createChartData(allActivities, dateRange);
const chartCodes = generateChartCode(chartData);

// 차트 출력
dv.paragraph(`### 활동 시간 차트`);
dv.paragraph(`#### 일별 활동 시간 (스택 막대 차트)`);
dv.paragraph(chartCodes.stackedBar);

dv.paragraph(`#### 활동별 총 시간 (파이 차트)`);
dv.paragraph(chartCodes.pie);

dv.paragraph(`#### 활동별 시간 추이 (라인 차트)`);
dv.paragraph(chartCodes.line);
```