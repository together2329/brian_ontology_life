---
project: grizzlyridge
epic: 
status:
---
```dataviewjs

```

```dataviewjs
// --- CONFIGURATION ---
// ⚠️ 중요: 아래 설정 값들을 자신의 Obsidian 환경에 맞게 정확히 수정해주세요!

// 📅 분석 기간 설정 (Date Range for Analysis)
const startDateRange = "2025-04-01"; // <--- !!! 시작 날짜 수정 !!!
const endDateRange = "2025-05-03";   // <--- !!! 종료 날짜 수정 !!!

// 📂 Task 파일들이 있는 폴더 경로 리스트 (List of Task Folder Paths)
const taskFolderPaths = [
    "02_Projects/Career/Grizzly Ridge/Task", // <--- 사용자 요청 경로 1
    "02_Projects/Career/Ratel2/Task",       // <--- 사용자 요청 경로 2
    "02_Projects/Career/Life Management Tool/Task", // <--- 사용자 요청 경로 3
    // "Tasks",
    // "02 - Areas/Action",
    // "Projects/My Project/Tasks"
];

// 📓 데일리 노트가 있는 폴더 경로 (Daily Notes Folder Path)
const dailyNoteFolder = "01_Daily/Daily"; // <--- !!! 자신의 데일리 노트 폴더 경로로 수정하세요 !!!

// ⭐ 동적 필터링: 아래 frontmatter 키를 사용하여 이 노트의 frontmatter에서 필터링합니다. ⭐
// --- 이 노트의 frontmatter에 다음 키를 추가하여 필터링하세요 ---
// project: "ProjectName1, ProjectName2"  (쉼표로 구분, 비워두면 모든 프로젝트 포함)
// epic: "EpicName1, EpicName2"        (쉼표로 구분, 비워두면 모든 Epic 포함)
// status: "Status1, Status2"         (쉼표로 구분하여 특정 상태 필터링. 비워두면 상태가 없는 Task만 필터링)
// 예시:
// ---
// project: "Grizzly Ridge"
// epic: "gzr"
// status: "In Progress, Review" // "In Progress" 또는 "Review" 상태인 Task 필터링
// ---
// ---
// project: "Ratel2"
// status:                     // status 필드가 비어있는 Task만 필터링
// ---
// --------------------------------------------------------------------

// --- DEBUGGING FLAGS ---
const enableVerboseLogging = true; // true로 설정하면 개발자 콘솔에 더 자세한 로그 출력

// --- CONSTANTS ---
const MINUTES_PER_HOUR = 60;
const MINUTES_PER_DAY = 24 * MINUTES_PER_HOUR; // 1일 = 24시간 기준

// --- FUNCTION DEFINITIONS ---

/**
 * 개발자 콘솔에 디버깅 메시지를 출력합니다.
 */
const logDebug = (message, data) => {
    if (enableVerboseLogging) {
        console.log(`[Dataview Debug] ${message}`, data !== undefined ? data : "");
    }
};

/**
 * 다양한 형식의 기간 문자열을 총 분(minute) 단위로 파싱합니다.
 */
const parseDurationToMinutes = (durationString) => {
    // ... (이전 코드와 동일) ...
    if (!durationString || typeof durationString !== 'string' || durationString.trim() === "" || durationString.trim() === "-") { return null; }
    durationString = durationString.trim(); let totalMinutes = 0;
    try {
        if (durationString.startsWith('P')) {
            let remainingString = durationString.substring(1); let timePart = remainingString.split('T')[1] || ''; let datePart = remainingString.split('T')[0];
            const dayMatch = datePart.match(/(\d+(\.\d+)?)D/); if (dayMatch) totalMinutes += parseFloat(dayMatch[1]) * MINUTES_PER_DAY;
            const hourMatch = timePart.match(/(\d+(\.\d+)?)H/); if (hourMatch) totalMinutes += parseFloat(hourMatch[1]) * MINUTES_PER_HOUR;
            const minuteMatch = timePart.match(/(\d+(\.\d+)?)M/); if (minuteMatch) totalMinutes += parseFloat(minuteMatch[1]);
            if (totalMinutes > 0 || dayMatch || hourMatch || minuteMatch) { return Math.round(totalMinutes); }
            logDebug(`parseDurationToMinutes (ISO): '${durationString}' 에서 유효 시간 단위 못찾음.`); totalMinutes = 0;
        }
        let combinedOrSimpleMinutes = 0; let matched = false;
        const parts = durationString.toLowerCase().match(/(\d+(\.\d+)?\s*[dhms])/g) || [];
        for (const part of parts) {
            const value = parseFloat(part); if (isNaN(value)) continue;
            if (part.includes('d')) { combinedOrSimpleMinutes += value * MINUTES_PER_DAY; matched = true;}
            else if (part.includes('h')) { combinedOrSimpleMinutes += value * MINUTES_PER_HOUR; matched = true;}
            else if (part.includes('m')) { combinedOrSimpleMinutes += value; matched = true; }
        }
         if (matched) { return Math.round(combinedOrSimpleMinutes); }
        const numberOnlyMatch = durationString.match(/^(\d+(\.\d+)?)$/);
        if (numberOnlyMatch) { totalMinutes = parseFloat(numberOnlyMatch[1]); return Math.round(totalMinutes); }
        logDebug(`parseDurationToMinutes: '${durationString}' 형식을 인식할 수 없음.`); return null;
    } catch (error) { dv.paragraph(`❌ **파싱 오류:** '${durationString}' 기간 파싱 중 오류 발생: ${error.message}`); logDebug("parseDurationToMinutes 오류 발생", error); return null; }
};

/**
 * 총 분(minute)을 "Xd Yh Zm" 형식의 문자열로 변환합니다.
 */
const formatMinutesToDHMS = (totalMinutes) => {
    // ... (이전 코드와 동일) ...
    if (totalMinutes === null || typeof totalMinutes !== 'number' || isNaN(totalMinutes)) { return "-"; }
    if (totalMinutes === 0) return "0m"; const sign = totalMinutes < 0 ? "-" : ""; let absMinutes = Math.abs(Math.round(totalMinutes));
    const days = Math.floor(absMinutes / MINUTES_PER_DAY); absMinutes %= MINUTES_PER_DAY;
    const hours = Math.floor(absMinutes / MINUTES_PER_HOUR); absMinutes %= MINUTES_PER_HOUR;
    const minutes = absMinutes; let result = "";
    if (days > 0) result += `${days}d `; if (hours > 0) result += `${hours}h `;
    if (minutes > 0 || (days === 0 && hours === 0)) { result += `${minutes}m`; }
    result = result.trim(); return result ? sign + result : "0m";
};

/**
 * YAML frontmatter 날짜 형식이 유효한지 확인합니다.
 */
const isValidDateString = (dateString) => {
    return /^\d{4}-\d{2}-\d{2}$/.test(dateString) && !isNaN(new Date(dateString));
};

/**
 * 숫자인지 확인하는 간단한 함수
 */
const isNumber = (value) => typeof value === 'number' && !isNaN(value);

/**
 * Frontmatter에서 필터 문자열을 파싱하여 소문자 배열로 반환합니다.
 */
const parseFilterString = (filterString) => {
    if (!filterString || typeof filterString !== 'string') {
        return [];
    }
    return filterString.split(',')          // 쉼표로 분리
                     .map(item => item.trim().toLowerCase()) // 공백 제거 및 소문자 변환
                     .filter(item => item !== ''); // 빈 항목 제거
};


// --- SCRIPT START ---
dv.paragraph("🚀 **Dataview Task Aggregator (Dynamic Filters + Status)**");

// ⭐ Frontmatter에서 동적 필터 값 읽기 (project, epic, status) ⭐
const currentNote = dv.current(); // 현재 노트의 정보 가져오기
const projectFilterInput = currentNote?.project || "";
const epicFilterInput = currentNote?.epic || "";
const statusFilterInput = currentNote?.status || ""; // status 필터 값 읽기

const projectFilter = parseFilterString(projectFilterInput);
const epicFilter = parseFilterString(epicFilterInput);
const statusFilter = parseFilterString(statusFilterInput); // status 필터 값 파싱

logDebug("스크립트 실행 시작", { startDateRange, endDateRange, taskFolderPaths, dailyNoteFolder });
logDebug("Frontmatter 필터 값:", { projectFilterInput, epicFilterInput, statusFilterInput });
logDebug("파싱된 필터:", { projectFilter, epicFilter, statusFilter });

// 날짜 범위 유효성 검사
if (!isValidDateString(startDateRange) || !isValidDateString(endDateRange)) {
    dv.paragraph(`❌ **설정 오류:** 시작 날짜(${startDateRange}) 또는 종료 날짜(${endDateRange}) 형식이 잘못되었습니다. "YYYY-MM-DD" 형식으로 입력해주세요.`);
    return;
}
const startDt = new Date(startDateRange);
const endDt = new Date(endDateRange);
endDt.setHours(23, 59, 59, 999);

if (startDt > endDt) {
    dv.paragraph(`❌ **설정 오류:** 시작 날짜(${startDateRange})가 종료 날짜(${endDateRange})보다 늦습니다.`);
    return;
}

// 1️⃣ Task 데이터 미리 가져오기 (Pre-fetch Task Data including Status)
const taskData = {};
let totalTasksLoaded = 0;
let foldersSearched = 0;
let foldersFound = [];
let foldersNotFound = [];
let foldersFailed = [];

if (!Array.isArray(taskFolderPaths) || taskFolderPaths.length === 0) {
     dv.paragraph(`❌ **설정 오류:** 'taskFolderPaths'가 유효한 배열이 아니거나 비어 있습니다.`);
} else {
    dv.paragraph(`🔍 Task 폴더 검색 시작 (${taskFolderPaths.length}개 경로): ${taskFolderPaths.join(', ')}`);
    for (const folderPath of taskFolderPaths) {
        const currentFolderPath = typeof folderPath === 'string' ? folderPath.trim() : '';
        if (!currentFolderPath) { foldersFailed.push("(빈 경로)"); continue; }
        try {
            const taskPages = dv.pages(`"${currentFolderPath}"`);
            foldersSearched++;
            if (taskPages.length > 0) {
                foldersFound.push(currentFolderPath);
                for (const taskPage of taskPages) {
                    const taskName = taskPage.file.name;
                    const taskFilePath = taskPage.file.path;
                    const estimatedTimeRaw = taskPage.estimated;
                    const projectRaw = taskPage.project;
                    const epicRaw = taskPage.epic;
                    const statusRaw = taskPage.status; // status 읽기
                    const impactRaw = taskPage.impact;

                    let impactNumber = null;
                    if (impactRaw !== undefined && impactRaw !== null) {
                        const parsedImpact = parseFloat(impactRaw);
                        if (!isNaN(parsedImpact)) { impactNumber = parsedImpact; }
                        else { logDebug(`'${taskName}' Task의 impact 값(${impactRaw})을 숫자로 파싱할 수 없음.`); }
                    }

                    const finalEstimatedRaw = (estimatedTimeRaw !== undefined && estimatedTimeRaw !== null && String(estimatedTimeRaw).trim() !== "") ? String(estimatedTimeRaw) : "-";
                    const finalProject = (projectRaw !== undefined && projectRaw !== null && String(projectRaw).trim() !== "") ? String(projectRaw) : "-";
                    const finalEpic = (epicRaw !== undefined && epicRaw !== null && String(epicRaw).trim() !== "") ? String(epicRaw) : "-";
                    // status가 없거나 비어있으면 "-" 로 통일
                    const finalStatus = (statusRaw !== undefined && statusRaw !== null && String(statusRaw).trim() !== "") ? String(statusRaw) : "-";

                    if (taskName) {
                        if (!taskData.hasOwnProperty(taskName)) {
                            taskData[taskName] = {
                                estimatedRaw: finalEstimatedRaw, project: finalProject, epic: finalEpic,
                                status: finalStatus, // status 저장
                                impact: impactNumber, sourcePath: taskFilePath
                            };
                            totalTasksLoaded++;
                        }
                    }
                }
            } else { foldersNotFound.push(currentFolderPath); }
        } catch (e) {
            dv.paragraph(`❌ **폴더 오류:** '${currentFolderPath}' 폴더 처리 중 오류 발생: ${e.message}. (경로 및 접근 권한 확인)`);
            logDebug(`폴더 처리 오류 (${currentFolderPath})`, e); foldersFailed.push(currentFolderPath);
        }
    }
    dv.paragraph(`✅ Task 로딩 완료: ${foldersSearched}개 폴더 검색 시도. ${foldersFound.length}개 폴더에서 ${totalTasksLoaded}개 고유 Task 로드.`);
    if (foldersNotFound.length > 0) dv.paragraph(`ℹ️ 파일 없음: ${foldersNotFound.join(', ')} 폴더에서는 Task 파일을 찾지 못했습니다.`);
    if (foldersFailed.length > 0) dv.paragraph(`❌ 로딩 실패 폴더: ${foldersFailed.join(', ')}.`);
    if (totalTasksLoaded === 0 && foldersSearched > 0 && foldersFailed.length === 0) dv.paragraph(`⚠️ **Task 없음:** 지정된 폴더들에서 유효한 Task 파일을 찾을 수 없습니다.`);
    if (taskFolderPaths.length > 1) dv.paragraph("ℹ️ *참고: 동일 이름 Task는 리스트에서 먼저 검색된 폴더의 정보 사용.*");
    logDebug("최종 로드된 Task 데이터:", taskData);
}

// 2️⃣ 지정된 기간 내 데일리 노트 처리 (Process Daily Notes within Date Range)
dv.paragraph(`📄 데일리 노트 분석 시작: ${dailyNoteFolder} 폴더 (${startDateRange} ~ ${endDateRange})`);
logDebug("분석할 데일리 노트 폴더:", dailyNoteFolder);

const allActivities = [];
let dailyNotesProcessed = 0;
let dailyNotesFailed = 0;
let totalDurationSkippedTasks = 0;

try {
    const dailyPages = dv.pages(`"${dailyNoteFolder}"`);
    logDebug(`${dailyNoteFolder} 폴더에서 ${dailyPages.length}개의 파일을 찾았습니다.`);

    for (const page of dailyPages) {
        const fileName = page.file.name;
        if (/^\d{4}-\d{2}-\d{2}$/.test(fileName)) {
            const currentNoteDateStr = fileName;
            const currentNoteDt = new Date(currentNoteDateStr);

            if (!isNaN(currentNoteDt) && currentNoteDt >= startDt && currentNoteDt <= endDt) {
                dailyNotesProcessed++;
                let fileContent = null;
                try { fileContent = await dv.io.load(page.file.path); }
                catch (e) { dv.paragraph(`❌ **파일 읽기 오류:** ${page.file.link} 내용 읽기 실패: ${e.message}.`); logDebug(`데일리 노트 파일 읽기 실패: ${page.file.path}`, e); dailyNotesFailed++; continue; }

                let sectionContent = null;
                if (fileContent !== null) {
                    const plannerHeader = "## Day planner";
                    const headerStartIndex = fileContent.toLowerCase().indexOf(plannerHeader.toLowerCase());
                    if (headerStartIndex !== -1) {
                        const contentAfterHeaderStart = fileContent.substring(headerStartIndex + plannerHeader.length);
                        const nextHeaderMatch = contentAfterHeaderStart.match(/^\s*#{2,}\s+/m);
                        const contentEndIndex = nextHeaderMatch ? nextHeaderMatch.index : contentAfterHeaderStart.length;
                        sectionContent = contentAfterHeaderStart.substring(0, contentEndIndex).trim();
                    }
                }

                if (sectionContent !== null && sectionContent.length > 0) {
                    const lines = sectionContent.split('\n');
                    const lineRegex = /^\s*(?:[-*•]\s+)?(\d{1,2}:\d{2})\s*[-–~]\s*(\d{1,2}:\d{2})\s+(.*?)(?:\s+#.*)?$/;
                    let timeErrors = 0;

                    for (const line of lines) {
                        const trimmedLine = line.trim();
                        if (!trimmedLine || trimmedLine.startsWith('#')) continue;
                        logDebug(`처리 시도 라인 (${page.file.name}):`, trimmedLine);

                        const match = trimmedLine.match(lineRegex);
                        if (match) {
                            logDebug(`   -> 정규식 매칭 성공!`);
                            let startTimeStr = match[1].padStart(5, '0');
                            let endTimeStr = match[2].padStart(5, '0');
                            let activityDisplay = match[3].trim();
                            let potentialTaskName = activityDisplay;
                            let estimatedRawResult = "-"; let projectResult = "-"; let epicResult = "-";
                            let statusResult = "-"; // status 변수 추가
                            let impactResult = null;

                            const linkMatch = activityDisplay.match(/^!?\[\[(.*?)\]\]$/);
                            if (linkMatch && linkMatch[1]) {
                                potentialTaskName = linkMatch[1].trim();
                                activityDisplay = linkMatch[0]; // Keep the link format for display
                            } else {
                                potentialTaskName = potentialTaskName
                                    .replace(/^\s*[\p{Emoji_Presentation}\p{Emoji}]\s*/u, '') // Remove leading emoji
                                    .replace(/^[ *_~]+|[ *_~]+$/g, '') // Trim markdown chars
                                    .replace(/[*_~]{1,3}(.*?)[*_~]{1,3}/g, '$1') // Remove surrounding markdown
                                    .trim();
                                activityDisplay = potentialTaskName; // Use cleaned name for display if not a link
                            }
                            logDebug(`   -> Task 이름 후보: '${potentialTaskName}'`);

                            let taskExists = false;
                            if (taskData.hasOwnProperty(potentialTaskName)) {
                                taskExists = true;
                                const taskInfo = taskData[potentialTaskName];
                                estimatedRawResult = taskInfo.estimatedRaw; projectResult = taskInfo.project;
                                epicResult = taskInfo.epic;
                                statusResult = taskInfo.status; // status 값 가져오기
                                impactResult = taskInfo.impact;
                                logDebug(`   -> Task 매칭됨: '${potentialTaskName}'`);
                            } else { logDebug(`   -> Task 매칭 안됨: '${potentialTaskName}'`); }

                            let durationMinutes = 0;
                             try {
                                const start = new Date(`${currentNoteDateStr}T${startTimeStr}:00`);
                                const end = new Date(`${currentNoteDateStr}T${endTimeStr}:00`);
                                if (isNaN(start.getTime()) || isNaN(end.getTime())) { logDebug(`   -> 시간 변환 오류`); timeErrors++; continue; }
                                if (start >= end) {
                                     logDebug(`   -> 종료 시간이 시작 시간보다 빠르거나 같음. 날짜 조정 시도.`);
                                     end.setDate(end.getDate() + 1);
                                     if (start >= end) { logDebug(`   -> 날짜 조정 후에도 시간 순서 오류. 건너뜀.`); timeErrors++; continue; }
                                }
                                durationMinutes = (end - start) / (1000 * 60);
                                logDebug(`   -> 계산된 시간: ${durationMinutes.toFixed(2)}분`);
                                if (durationMinutes <= 0) continue;
                            } catch (e) { dv.paragraph(`❌ **시간 처리 오류:** ${page.file.link}의 '${trimmedLine}' 처리 중 오류: ${e.message}`); logDebug(`시간 처리 예외 발생 (${page.file.name}): ${trimmedLine}`, e); timeErrors++; continue; }

                            if (taskExists) {
                                if (!activityDisplay) activityDisplay = "(설명 없음)";
                                allActivities.push({
                                    activityDisplay, duration: Math.round(durationMinutes),
                                    estimatedRaw: estimatedRawResult, project: projectResult, epic: epicResult,
                                    status: statusResult, // status 추가
                                    impact: impactResult
                                });
                                logDebug(`   => 활동 추가됨 (Task 존재): '${activityDisplay}', duration: ${Math.round(durationMinutes)}`);
                            } else {
                                totalDurationSkippedTasks += durationMinutes;
                                logDebug(`   => 활동 건너뜀 (Task 없음): '${activityDisplay}', 시간: ${durationMinutes.toFixed(2)}분`);
                            }
                        } else { logDebug("   -> 정규식 매칭 실패 (처리 안함)"); }
                    } // End of line loop
                     if (timeErrors > 0) dv.paragraph(`⚠️ ${page.file.link} 처리 중 ${timeErrors}개의 시간 관련 오류/경고 발생.`);
                }
            }
        }
    } // End of page loop

    dv.paragraph(`✅ 데일리 노트 처리 완료: 총 ${dailyNotesProcessed}개 파일 분석 완료. ${dailyNotesFailed}개 파일 읽기 실패.`);
    if (totalDurationSkippedTasks > 0) {
         dv.paragraph(`ℹ️ **참고:** Task 파일이 없어 집계에서 제외된 활동들의 총 시간은 약 ${formatMinutesToDHMS(totalDurationSkippedTasks)} 입니다.`);
    }

} catch (e) {
    dv.paragraph(`❌ **폴더 처리 오류:** 데일리 노트 폴더('${dailyNoteFolder}') 처리 중 오류 발생: ${e.message}.`);
    logDebug(`데일리 노트 폴더 처리 오류`, e);
}


// 3️⃣ 최종 결과 집계 및 출력 (Aggregate Final Results and Render)
if (allActivities.length > 0) {
    logDebug("최종 결과 집계 시작. Task와 매칭된 활동 항목 수:", allActivities.length);

    const grouped = allActivities.reduce((acc, { activityDisplay, duration, estimatedRaw, project, epic, status, impact }) => { // status 추가
        if (!acc[activityDisplay]) {
            acc[activityDisplay] = { totalDuration: 0, estimatedRaw: estimatedRaw, project: project, epic: epic, status: status, impact: impact }; // status 추가
        }
        // Use the first non-empty value found for metadata
        if (!acc[activityDisplay].estimatedRaw || acc[activityDisplay].estimatedRaw === "-") acc[activityDisplay].estimatedRaw = estimatedRaw;
        if (!acc[activityDisplay].project || acc[activityDisplay].project === "-") acc[activityDisplay].project = project;
        if (!acc[activityDisplay].epic || acc[activityDisplay].epic === "-") acc[activityDisplay].epic = epic;
        // status는 항상 마지막 값으로 덮어쓰거나, 초기값("-")을 유지하도록 수정
        if (status !== "-") acc[activityDisplay].status = status;
        else if (!acc[activityDisplay].status) acc[activityDisplay].status = "-"; // 초기값이 없으면 "-" 로 설정

        if (!isNumber(acc[activityDisplay].impact) && isNumber(impact)) acc[activityDisplay].impact = impact;
        acc[activityDisplay].totalDuration += duration;
        return acc;
    }, {});
    logDebug("최종 활동별 집계 결과 (Task 존재하는 것만):", grouped);

    // ⭐ 프로젝트, Epic, Status 필터링 적용 (Status 로직 수정) ⭐
    const filteredGroupedEntries = Object.entries(grouped).filter(([activity, data]) => {
        const projectMatch = projectFilter.length === 0 || projectFilter.includes(data.project.toLowerCase());
        const epicMatch = epicFilter.length === 0 || epicFilter.includes(data.epic.toLowerCase());
        // Status 필터 로직 수정
        const statusMatch = statusFilter.length === 0
            ? data.status === "-" // Frontmatter status 필터가 비어있으면, status가 없는 ("-") Task만 매칭
            : statusFilter.includes(data.status.toLowerCase()); // Frontmatter status 필터가 있으면, 해당 status 매칭

        return projectMatch && epicMatch && statusMatch; // 모든 활성 필터 만족해야 함
    });
    logDebug("프로젝트/Epic/Status 필터링 후 항목 수:", filteredGroupedEntries.length);

    if (filteredGroupedEntries.length > 0) {
        let totalPositiveRemainingMinutes = 0;
        let totalActualMinutesSum = 0;
        let totalEstimatedMinutesSum = 0;

        const dataForTable = filteredGroupedEntries.map(([activity, data]) => {
            const estimatedMinutes = parseDurationToMinutes(data.estimatedRaw);
            const impact = data.impact;
            let priority = -Infinity;
            if (isNumber(impact) && isNumber(estimatedMinutes) && estimatedMinutes > 0) {
                priority = impact / estimatedMinutes;
            }

            let remainingMinutes = null;
            if (isNumber(estimatedMinutes)) {
                remainingMinutes = estimatedMinutes - data.totalDuration;
                if (remainingMinutes > 0) {
                    totalPositiveRemainingMinutes += remainingMinutes;
                }
                totalEstimatedMinutesSum += estimatedMinutes;
            }
            totalActualMinutesSum += data.totalDuration;

            return {
                activity, project: data.project, epic: data.epic, status: data.status, // status 추가
                impact: isNumber(impact) ? impact : "-",
                totalDurationMinutes: data.totalDuration,
                estimatedMinutes: estimatedMinutes,
                priority: priority,
                remainingMinutes: remainingMinutes
            };
        });

        dataForTable.sort((a, b) => b.priority - a.priority); // Sort by Priority descending
        logDebug("Priority 기준 정렬 후 데이터:", dataForTable);

        // 필터링 정보 표시 업데이트
        let filterSummary = "";
        if (projectFilter.length > 0) filterSummary += `**프로젝트:** ${projectFilterInput || projectFilter.join(', ')}`;
        if (epicFilter.length > 0) {
            if (filterSummary) filterSummary += " | ";
            filterSummary += `**Epic:** ${epicFilterInput || epicFilter.join(', ')}`;
        }
        if (statusFilter.length > 0) { // status 필터 요약 추가
             if (filterSummary) filterSummary += " | ";
             filterSummary += `**Status:** ${statusFilterInput || statusFilter.join(', ')}`;
        } else {
             // status 필터가 비어있을 때 "상태 없음" 표시
             if (filterSummary) filterSummary += " | ";
             filterSummary += `**Status:** (상태 없음)`;
        }


        if (filterSummary) {
             dv.paragraph(`--- **필터링 조건:** ${filterSummary} ---`);
        } else {
             // 모든 필터가 비어있는 경우 (project, epic 비어있고 status도 비어있어 "상태 없음"만 필터링)
             dv.paragraph(`--- 전체 기간 활동 요약 (${startDateRange} ~ ${endDateRange}) ---`);
             dv.paragraph(`--- **필터링 조건:** **Status:** (상태 없음) ---`); // 상태 없음 필터링 명시
        }

        // 테이블 헤더 수정
        const header = `| 활동 (Activity) | Project | Epic | Status | Impact | Priority | 총 소요 시간 (Total) | 예상 시간 (Estimated) | 남은 시간 (Remaining) |
| :-------------- | :------ | :--- | :----- | :----- | :------- | :------------------- | :-------------------- | :-------------------- |`; // Status 열 추가

        // 테이블 행 생성 수정
        const rows = dataForTable.map(item => {
            const totalFormatted = formatMinutesToDHMS(item.totalDurationMinutes);
            const estimatedFormatted = formatMinutesToDHMS(item.estimatedMinutes);
            const remainingTimeToFormat = isNumber(item.remainingMinutes) && item.remainingMinutes < 0 ? 0 : item.remainingMinutes;
            const remainingFormatted = formatMinutesToDHMS(remainingTimeToFormat);
            const priorityFormatted = isFinite(item.priority) && item.priority > -Infinity ? item.priority.toFixed(2) : "-";
            const escapePipe = (str) => String(str).replace(/\|/g, "\\|");

            // Status 열 추가
            return `| ${escapePipe(item.activity)} | ${escapePipe(item.project)} | ${escapePipe(item.epic)} | ${escapePipe(item.status)} | ${escapePipe(item.impact)} | ${priorityFormatted} | ${totalFormatted} | ${estimatedFormatted} | ${remainingFormatted} |`;
        });

        // 테이블 합계 행 수정
        const totalActualFormatted = formatMinutesToDHMS(totalActualMinutesSum);
        const totalEstimatedFormatted = formatMinutesToDHMS(totalEstimatedMinutesSum);
        const totalRemainingFormatted = formatMinutesToDHMS(totalPositiveRemainingMinutes);
        const totalRow = `| **총 합계** | | | | | | **${totalActualFormatted}** | **${totalEstimatedFormatted}** | **${totalRemainingFormatted}** |`; // Status 열에 빈 칸 추가

        dv.paragraph(header + "\n" + rows.join("\n") + "\n" + totalRow);

    } else {
        // 필터링 결과 데이터가 없는 경우 메시지 업데이트
        let filterMsg = "";
        if (projectFilter.length > 0) filterMsg += `프로젝트(${projectFilterInput || projectFilter.join(', ')})`;
        if (epicFilter.length > 0) {
             if (filterMsg) filterMsg += " 및 ";
             filterMsg += `Epic(${epicFilterInput || epicFilter.join(', ')})`;
        }
         if (statusFilter.length > 0) { // status 필터 메시지 추가
             if (filterMsg) filterMsg += " 및 ";
             filterMsg += `Status(${statusFilterInput || statusFilter.join(', ')})`;
         } else {
             // status 필터가 비어있을 때 "상태 없음" 메시지 추가
             if (filterMsg) filterMsg += " 및 ";
             filterMsg += `Status(상태 없음)`;
         }

        if (filterMsg) {
             dv.paragraph(`ℹ️ 선택된 ${filterMsg} 조건에 해당하는 활동 로그를 찾지 못했습니다.`);
        } else {
             // 이 경우는 모든 필터가 비어있을 때 발생 가능 (상태 없는 Task가 없을 때)
             dv.paragraph("ℹ️ 유효한 활동 그룹이 없습니다 (Task와 매칭된 활동 없음).");
        }
    }
} else {
    dv.paragraph(`ℹ️ 지정된 기간(${startDateRange} ~ ${endDateRange}) 내 '${dailyNoteFolder}' 폴더에서 Task와 매칭되는 활동 로그를 찾지 못했습니다.`);
}

dv.paragraph("🏁 **스크립트 실행 종료**");
logDebug("스크립트 실행 종료.");
// --- SCRIPT END ---

```

```dataviewjs
// --- CONFIGURATION ---
// ⚠️ 중요: 아래 설정 값들을 자신의 Obsidian 환경에 맞게 정확히 수정해주세요!

// 📅 분석 기간 설정 (Date Range for Analysis)
const startDateRange = "2025-04-01"; // <--- !!! 시작 날짜 수정 !!!
const endDateRange = "2025-05-03";   // <--- !!! 종료 날짜 수정 !!!

// 📂 Task 파일들이 있는 폴더 경로 리스트 (List of Task Folder Paths)
const taskFolderPaths = [
    "02_Projects/Career/Grizzly Ridge/Task", // <--- 사용자 요청 경로 1
    "02_Projects/Career/Ratel2/Task",       // <--- 사용자 요청 경로 2
    "02_Projects/Career/Life Management Tool/Task", // <--- 사용자 요청 경로 3
    // "Tasks",
    // "02 - Areas/Action",
    // "Projects/My Project/Tasks"
];

// 📓 데일리 노트가 있는 폴더 경로 (Daily Notes Folder Path)
const dailyNoteFolder = "01_Daily/Daily"; // <--- !!! 자신의 데일리 노트 폴더 경로로 수정하세요 !!!

// ⭐ 동적 필터링: 아래 frontmatter 키를 사용하여 이 노트의 frontmatter에서 필터링합니다. ⭐
// --- 이 노트의 frontmatter에 다음 키를 추가하여 필터링하세요 ---
// project: "ProjectName1, ProjectName2"  (쉼표로 구분, 비워두면 모든 프로젝트 포함)
// epic: "EpicName1, EpicName2"        (쉼표로 구분, 비워두면 모든 Epic 포함)
// status: "Status1, Status2"         (쉼표로 구분, 비워두면 모든 상태 포함. 예: "In Progress, Done")
// 예시:
// ---
// project: "Grizzly Ridge"
// epic: "gzr"
// status: "In Progress, Review"
// ---
// --------------------------------------------------------------------

// --- DEBUGGING FLAGS ---
const enableVerboseLogging = true; // true로 설정하면 개발자 콘솔에 더 자세한 로그 출력

// --- CONSTANTS ---
const MINUTES_PER_HOUR = 60;
const MINUTES_PER_DAY = 24 * MINUTES_PER_HOUR; // 1일 = 24시간 기준

// --- FUNCTION DEFINITIONS ---

/**
 * 개발자 콘솔에 디버깅 메시지를 출력합니다.
 */
const logDebug = (message, data) => {
    if (enableVerboseLogging) {
        console.log(`[Dataview Debug] ${message}`, data !== undefined ? data : "");
    }
};

/**
 * 다양한 형식의 기간 문자열을 총 분(minute) 단위로 파싱합니다.
 */
const parseDurationToMinutes = (durationString) => {
    // ... (이전 코드와 동일) ...
    if (!durationString || typeof durationString !== 'string' || durationString.trim() === "" || durationString.trim() === "-") { return null; }
    durationString = durationString.trim(); let totalMinutes = 0;
    try {
        if (durationString.startsWith('P')) {
            let remainingString = durationString.substring(1); let timePart = remainingString.split('T')[1] || ''; let datePart = remainingString.split('T')[0];
            const dayMatch = datePart.match(/(\d+(\.\d+)?)D/); if (dayMatch) totalMinutes += parseFloat(dayMatch[1]) * MINUTES_PER_DAY;
            const hourMatch = timePart.match(/(\d+(\.\d+)?)H/); if (hourMatch) totalMinutes += parseFloat(hourMatch[1]) * MINUTES_PER_HOUR;
            const minuteMatch = timePart.match(/(\d+(\.\d+)?)M/); if (minuteMatch) totalMinutes += parseFloat(minuteMatch[1]);
            if (totalMinutes > 0 || dayMatch || hourMatch || minuteMatch) { return Math.round(totalMinutes); }
            logDebug(`parseDurationToMinutes (ISO): '${durationString}' 에서 유효 시간 단위 못찾음.`); totalMinutes = 0;
        }
        let combinedOrSimpleMinutes = 0; let matched = false;
        const parts = durationString.toLowerCase().match(/(\d+(\.\d+)?\s*[dhms])/g) || [];
        for (const part of parts) {
            const value = parseFloat(part); if (isNaN(value)) continue;
            if (part.includes('d')) { combinedOrSimpleMinutes += value * MINUTES_PER_DAY; matched = true;}
            else if (part.includes('h')) { combinedOrSimpleMinutes += value * MINUTES_PER_HOUR; matched = true;}
            else if (part.includes('m')) { combinedOrSimpleMinutes += value; matched = true; }
        }
         if (matched) { return Math.round(combinedOrSimpleMinutes); }
        const numberOnlyMatch = durationString.match(/^(\d+(\.\d+)?)$/);
        if (numberOnlyMatch) { totalMinutes = parseFloat(numberOnlyMatch[1]); return Math.round(totalMinutes); }
        logDebug(`parseDurationToMinutes: '${durationString}' 형식을 인식할 수 없음.`); return null;
    } catch (error) { dv.paragraph(`❌ **파싱 오류:** '${durationString}' 기간 파싱 중 오류 발생: ${error.message}`); logDebug("parseDurationToMinutes 오류 발생", error); return null; }
};

/**
 * 총 분(minute)을 "Xd Yh Zm" 형식의 문자열로 변환합니다.
 */
const formatMinutesToDHMS = (totalMinutes) => {
    // ... (이전 코드와 동일) ...
    if (totalMinutes === null || typeof totalMinutes !== 'number' || isNaN(totalMinutes)) { return "-"; }
    if (totalMinutes === 0) return "0m"; const sign = totalMinutes < 0 ? "-" : ""; let absMinutes = Math.abs(Math.round(totalMinutes));
    const days = Math.floor(absMinutes / MINUTES_PER_DAY); absMinutes %= MINUTES_PER_DAY;
    const hours = Math.floor(absMinutes / MINUTES_PER_HOUR); absMinutes %= MINUTES_PER_HOUR;
    const minutes = absMinutes; let result = "";
    if (days > 0) result += `${days}d `; if (hours > 0) result += `${hours}h `;
    if (minutes > 0 || (days === 0 && hours === 0)) { result += `${minutes}m`; }
    result = result.trim(); return result ? sign + result : "0m";
};

/**
 * YAML frontmatter 날짜 형식이 유효한지 확인합니다.
 */
const isValidDateString = (dateString) => {
    return /^\d{4}-\d{2}-\d{2}$/.test(dateString) && !isNaN(new Date(dateString));
};

/**
 * 숫자인지 확인하는 간단한 함수
 */
const isNumber = (value) => typeof value === 'number' && !isNaN(value);

/**
 * Frontmatter에서 필터 문자열을 파싱하여 소문자 배열로 반환합니다.
 */
const parseFilterString = (filterString) => {
    if (!filterString || typeof filterString !== 'string') {
        return [];
    }
    return filterString.split(',')          // 쉼표로 분리
                     .map(item => item.trim().toLowerCase()) // 공백 제거 및 소문자 변환
                     .filter(item => item !== ''); // 빈 항목 제거
};


// --- SCRIPT START ---
dv.paragraph("🚀 **Dataview Task Aggregator (Dynamic Filters + Status)**");

// ⭐ Frontmatter에서 동적 필터 값 읽기 (project, epic, status) ⭐
const currentNote = dv.current(); // 현재 노트의 정보 가져오기
const projectFilterInput = currentNote?.project || "";
const epicFilterInput = currentNote?.epic || "";
const statusFilterInput = currentNote?.status || ""; // status 필터 값 읽기

const projectFilter = parseFilterString(projectFilterInput);
const epicFilter = parseFilterString(epicFilterInput);
const statusFilter = parseFilterString(statusFilterInput); // status 필터 값 파싱

logDebug("스크립트 실행 시작", { startDateRange, endDateRange, taskFolderPaths, dailyNoteFolder });
logDebug("Frontmatter 필터 값:", { projectFilterInput, epicFilterInput, statusFilterInput });
logDebug("파싱된 필터:", { projectFilter, epicFilter, statusFilter });

// 날짜 범위 유효성 검사
if (!isValidDateString(startDateRange) || !isValidDateString(endDateRange)) {
    dv.paragraph(`❌ **설정 오류:** 시작 날짜(${startDateRange}) 또는 종료 날짜(${endDateRange}) 형식이 잘못되었습니다. "YYYY-MM-DD" 형식으로 입력해주세요.`);
    return;
}
const startDt = new Date(startDateRange);
const endDt = new Date(endDateRange);
endDt.setHours(23, 59, 59, 999);

if (startDt > endDt) {
    dv.paragraph(`❌ **설정 오류:** 시작 날짜(${startDateRange})가 종료 날짜(${endDateRange})보다 늦습니다.`);
    return;
}

// 1️⃣ Task 데이터 미리 가져오기 (Pre-fetch Task Data including Status)
const taskData = {};
let totalTasksLoaded = 0;
let foldersSearched = 0;
let foldersFound = [];
let foldersNotFound = [];
let foldersFailed = [];

if (!Array.isArray(taskFolderPaths) || taskFolderPaths.length === 0) {
     dv.paragraph(`❌ **설정 오류:** 'taskFolderPaths'가 유효한 배열이 아니거나 비어 있습니다.`);
} else {
    dv.paragraph(`🔍 Task 폴더 검색 시작 (${taskFolderPaths.length}개 경로): ${taskFolderPaths.join(', ')}`);
    for (const folderPath of taskFolderPaths) {
        const currentFolderPath = typeof folderPath === 'string' ? folderPath.trim() : '';
        if (!currentFolderPath) { foldersFailed.push("(빈 경로)"); continue; }
        try {
            const taskPages = dv.pages(`"${currentFolderPath}"`);
            foldersSearched++;
            if (taskPages.length > 0) {
                foldersFound.push(currentFolderPath);
                for (const taskPage of taskPages) {
                    const taskName = taskPage.file.name;
                    const taskFilePath = taskPage.file.path;
                    const estimatedTimeRaw = taskPage.estimated;
                    const projectRaw = taskPage.project;
                    const epicRaw = taskPage.epic;
                    const statusRaw = taskPage.status; // status 읽기
                    const impactRaw = taskPage.impact;

                    let impactNumber = null;
                    if (impactRaw !== undefined && impactRaw !== null) {
                        const parsedImpact = parseFloat(impactRaw);
                        if (!isNaN(parsedImpact)) { impactNumber = parsedImpact; }
                        else { logDebug(`'${taskName}' Task의 impact 값(${impactRaw})을 숫자로 파싱할 수 없음.`); }
                    }

                    const finalEstimatedRaw = (estimatedTimeRaw !== undefined && estimatedTimeRaw !== null && String(estimatedTimeRaw).trim() !== "") ? String(estimatedTimeRaw) : "-";
                    const finalProject = (projectRaw !== undefined && projectRaw !== null && String(projectRaw).trim() !== "") ? String(projectRaw) : "-";
                    const finalEpic = (epicRaw !== undefined && epicRaw !== null && String(epicRaw).trim() !== "") ? String(epicRaw) : "-";
                    const finalStatus = (statusRaw !== undefined && statusRaw !== null && String(statusRaw).trim() !== "") ? String(statusRaw) : "-"; // status 기본값 처리

                    if (taskName) {
                        if (!taskData.hasOwnProperty(taskName)) {
                            taskData[taskName] = {
                                estimatedRaw: finalEstimatedRaw, project: finalProject, epic: finalEpic,
                                status: finalStatus, // status 저장
                                impact: impactNumber, sourcePath: taskFilePath
                            };
                            totalTasksLoaded++;
                        }
                    }
                }
            } else { foldersNotFound.push(currentFolderPath); }
        } catch (e) {
            dv.paragraph(`❌ **폴더 오류:** '${currentFolderPath}' 폴더 처리 중 오류 발생: ${e.message}. (경로 및 접근 권한 확인)`);
            logDebug(`폴더 처리 오류 (${currentFolderPath})`, e); foldersFailed.push(currentFolderPath);
        }
    }
    dv.paragraph(`✅ Task 로딩 완료: ${foldersSearched}개 폴더 검색 시도. ${foldersFound.length}개 폴더에서 ${totalTasksLoaded}개 고유 Task 로드.`);
    if (foldersNotFound.length > 0) dv.paragraph(`ℹ️ 파일 없음: ${foldersNotFound.join(', ')} 폴더에서는 Task 파일을 찾지 못했습니다.`);
    if (foldersFailed.length > 0) dv.paragraph(`❌ 로딩 실패 폴더: ${foldersFailed.join(', ')}.`);
    if (totalTasksLoaded === 0 && foldersSearched > 0 && foldersFailed.length === 0) dv.paragraph(`⚠️ **Task 없음:** 지정된 폴더들에서 유효한 Task 파일을 찾을 수 없습니다.`);
    if (taskFolderPaths.length > 1) dv.paragraph("ℹ️ *참고: 동일 이름 Task는 리스트에서 먼저 검색된 폴더의 정보 사용.*");
    logDebug("최종 로드된 Task 데이터:", taskData);
}

// 2️⃣ 지정된 기간 내 데일리 노트 처리 (Process Daily Notes within Date Range)
dv.paragraph(`📄 데일리 노트 분석 시작: ${dailyNoteFolder} 폴더 (${startDateRange} ~ ${endDateRange})`);
logDebug("분석할 데일리 노트 폴더:", dailyNoteFolder);

const allActivities = [];
let dailyNotesProcessed = 0;
let dailyNotesFailed = 0;
let totalDurationSkippedTasks = 0;

try {
    const dailyPages = dv.pages(`"${dailyNoteFolder}"`);
    logDebug(`${dailyNoteFolder} 폴더에서 ${dailyPages.length}개의 파일을 찾았습니다.`);

    for (const page of dailyPages) {
        const fileName = page.file.name;
        if (/^\d{4}-\d{2}-\d{2}$/.test(fileName)) {
            const currentNoteDateStr = fileName;
            const currentNoteDt = new Date(currentNoteDateStr);

            if (!isNaN(currentNoteDt) && currentNoteDt >= startDt && currentNoteDt <= endDt) {
                dailyNotesProcessed++;
                let fileContent = null;
                try { fileContent = await dv.io.load(page.file.path); }
                catch (e) { dv.paragraph(`❌ **파일 읽기 오류:** ${page.file.link} 내용 읽기 실패: ${e.message}.`); logDebug(`데일리 노트 파일 읽기 실패: ${page.file.path}`, e); dailyNotesFailed++; continue; }

                let sectionContent = null;
                if (fileContent !== null) {
                    const plannerHeader = "## Day planner";
                    const headerStartIndex = fileContent.toLowerCase().indexOf(plannerHeader.toLowerCase());
                    if (headerStartIndex !== -1) {
                        const contentAfterHeaderStart = fileContent.substring(headerStartIndex + plannerHeader.length);
                        const nextHeaderMatch = contentAfterHeaderStart.match(/^\s*#{2,}\s+/m);
                        const contentEndIndex = nextHeaderMatch ? nextHeaderMatch.index : contentAfterHeaderStart.length;
                        sectionContent = contentAfterHeaderStart.substring(0, contentEndIndex).trim();
                    }
                }

                if (sectionContent !== null && sectionContent.length > 0) {
                    const lines = sectionContent.split('\n');
                    const lineRegex = /^\s*(?:[-*•]\s+)?(\d{1,2}:\d{2})\s*[-–~]\s*(\d{1,2}:\d{2})\s+(.*?)(?:\s+#.*)?$/;
                    let timeErrors = 0;

                    for (const line of lines) {
                        const trimmedLine = line.trim();
                        if (!trimmedLine || trimmedLine.startsWith('#')) continue;
                        logDebug(`처리 시도 라인 (${page.file.name}):`, trimmedLine);

                        const match = trimmedLine.match(lineRegex);
                        if (match) {
                            logDebug(`   -> 정규식 매칭 성공!`);
                            let startTimeStr = match[1].padStart(5, '0');
                            let endTimeStr = match[2].padStart(5, '0');
                            let activityDisplay = match[3].trim();
                            let potentialTaskName = activityDisplay;
                            let estimatedRawResult = "-"; let projectResult = "-"; let epicResult = "-";
                            let statusResult = "-"; // status 변수 추가
                            let impactResult = null;

                            const linkMatch = activityDisplay.match(/^!?\[\[(.*?)\]\]$/);
                            if (linkMatch && linkMatch[1]) {
                                potentialTaskName = linkMatch[1].trim();
                                activityDisplay = linkMatch[0]; // Keep the link format for display
                            } else {
                                potentialTaskName = potentialTaskName
                                    .replace(/^\s*[\p{Emoji_Presentation}\p{Emoji}]\s*/u, '') // Remove leading emoji
                                    .replace(/^[ *_~]+|[ *_~]+$/g, '') // Trim markdown chars
                                    .replace(/[*_~]{1,3}(.*?)[*_~]{1,3}/g, '$1') // Remove surrounding markdown
                                    .trim();
                                activityDisplay = potentialTaskName; // Use cleaned name for display if not a link
                            }
                            logDebug(`   -> Task 이름 후보: '${potentialTaskName}'`);

                            let taskExists = false;
                            if (taskData.hasOwnProperty(potentialTaskName)) {
                                taskExists = true;
                                const taskInfo = taskData[potentialTaskName];
                                estimatedRawResult = taskInfo.estimatedRaw; projectResult = taskInfo.project;
                                epicResult = taskInfo.epic;
                                statusResult = taskInfo.status; // status 값 가져오기
                                impactResult = taskInfo.impact;
                                logDebug(`   -> Task 매칭됨: '${potentialTaskName}'`);
                            } else { logDebug(`   -> Task 매칭 안됨: '${potentialTaskName}'`); }

                            let durationMinutes = 0;
                             try {
                                const start = new Date(`${currentNoteDateStr}T${startTimeStr}:00`);
                                const end = new Date(`${currentNoteDateStr}T${endTimeStr}:00`);
                                if (isNaN(start.getTime()) || isNaN(end.getTime())) { logDebug(`   -> 시간 변환 오류`); timeErrors++; continue; }
                                if (start >= end) {
                                     logDebug(`   -> 종료 시간이 시작 시간보다 빠르거나 같음. 날짜 조정 시도.`);
                                     end.setDate(end.getDate() + 1);
                                     if (start >= end) { logDebug(`   -> 날짜 조정 후에도 시간 순서 오류. 건너뜀.`); timeErrors++; continue; }
                                }
                                durationMinutes = (end - start) / (1000 * 60);
                                logDebug(`   -> 계산된 시간: ${durationMinutes.toFixed(2)}분`);
                                if (durationMinutes <= 0) continue;
                            } catch (e) { dv.paragraph(`❌ **시간 처리 오류:** ${page.file.link}의 '${trimmedLine}' 처리 중 오류: ${e.message}`); logDebug(`시간 처리 예외 발생 (${page.file.name}): ${trimmedLine}`, e); timeErrors++; continue; }

                            if (taskExists) {
                                if (!activityDisplay) activityDisplay = "(설명 없음)";
                                allActivities.push({
                                    activityDisplay, duration: Math.round(durationMinutes),
                                    estimatedRaw: estimatedRawResult, project: projectResult, epic: epicResult,
                                    status: statusResult, // status 추가
                                    impact: impactResult
                                });
                                logDebug(`   => 활동 추가됨 (Task 존재): '${activityDisplay}', duration: ${Math.round(durationMinutes)}`);
                            } else {
                                totalDurationSkippedTasks += durationMinutes;
                                logDebug(`   => 활동 건너뜀 (Task 없음): '${activityDisplay}', 시간: ${durationMinutes.toFixed(2)}분`);
                            }
                        } else { logDebug("   -> 정규식 매칭 실패 (처리 안함)"); }
                    } // End of line loop
                     if (timeErrors > 0) dv.paragraph(`⚠️ ${page.file.link} 처리 중 ${timeErrors}개의 시간 관련 오류/경고 발생.`);
                }
            }
        }
    } // End of page loop

    dv.paragraph(`✅ 데일리 노트 처리 완료: 총 ${dailyNotesProcessed}개 파일 분석 완료. ${dailyNotesFailed}개 파일 읽기 실패.`);
    if (totalDurationSkippedTasks > 0) {
         dv.paragraph(`ℹ️ **참고:** Task 파일이 없어 집계에서 제외된 활동들의 총 시간은 약 ${formatMinutesToDHMS(totalDurationSkippedTasks)} 입니다.`);
    }

} catch (e) {
    dv.paragraph(`❌ **폴더 처리 오류:** 데일리 노트 폴더('${dailyNoteFolder}') 처리 중 오류 발생: ${e.message}.`);
    logDebug(`데일리 노트 폴더 처리 오류`, e);
}


// 3️⃣ 최종 결과 집계 및 출력 (Aggregate Final Results and Render)
if (allActivities.length > 0) {
    logDebug("최종 결과 집계 시작. Task와 매칭된 활동 항목 수:", allActivities.length);

    const grouped = allActivities.reduce((acc, { activityDisplay, duration, estimatedRaw, project, epic, status, impact }) => { // status 추가
        if (!acc[activityDisplay]) {
            acc[activityDisplay] = { totalDuration: 0, estimatedRaw: estimatedRaw, project: project, epic: epic, status: status, impact: impact }; // status 추가
        }
        // Use the first non-empty value found for metadata
        if (!acc[activityDisplay].estimatedRaw || acc[activityDisplay].estimatedRaw === "-") acc[activityDisplay].estimatedRaw = estimatedRaw;
        if (!acc[activityDisplay].project || acc[activityDisplay].project === "-") acc[activityDisplay].project = project;
        if (!acc[activityDisplay].epic || acc[activityDisplay].epic === "-") acc[activityDisplay].epic = epic;
        if (!acc[activityDisplay].status || acc[activityDisplay].status === "-") acc[activityDisplay].status = status; // status 처리
        if (!isNumber(acc[activityDisplay].impact) && isNumber(impact)) acc[activityDisplay].impact = impact;
        acc[activityDisplay].totalDuration += duration;
        return acc;
    }, {});
    logDebug("최종 활동별 집계 결과 (Task 존재하는 것만):", grouped);

    // ⭐ 프로젝트, Epic, Status 필터링 적용 ⭐
    const filteredGroupedEntries = Object.entries(grouped).filter(([activity, data]) => {
        const projectMatch = projectFilter.length === 0 || projectFilter.includes(data.project.toLowerCase());
        const epicMatch = epicFilter.length === 0 || epicFilter.includes(data.epic.toLowerCase());
        const statusMatch = statusFilter.length === 0 || statusFilter.includes(data.status.toLowerCase()); // status 필터 조건 추가
        return projectMatch && epicMatch && statusMatch; // 모든 활성 필터 만족해야 함
    });
    logDebug("프로젝트/Epic/Status 필터링 후 항목 수:", filteredGroupedEntries.length);

    if (filteredGroupedEntries.length > 0) {
        let totalPositiveRemainingMinutes = 0;
        let totalActualMinutesSum = 0;
        let totalEstimatedMinutesSum = 0;

        const dataForTable = filteredGroupedEntries.map(([activity, data]) => {
            const estimatedMinutes = parseDurationToMinutes(data.estimatedRaw);
            const impact = data.impact;
            let priority = -Infinity;
            if (isNumber(impact) && isNumber(estimatedMinutes) && estimatedMinutes > 0) {
                priority = impact / estimatedMinutes;
            }

            let remainingMinutes = null;
            if (isNumber(estimatedMinutes)) {
                remainingMinutes = estimatedMinutes - data.totalDuration;
                if (remainingMinutes > 0) {
                    totalPositiveRemainingMinutes += remainingMinutes;
                }
                totalEstimatedMinutesSum += estimatedMinutes;
            }
            totalActualMinutesSum += data.totalDuration;

            return {
                activity, project: data.project, epic: data.epic, status: data.status, // status 추가
                impact: isNumber(impact) ? impact : "-",
                totalDurationMinutes: data.totalDuration,
                estimatedMinutes: estimatedMinutes,
                priority: priority,
                remainingMinutes: remainingMinutes
            };
        });

        dataForTable.sort((a, b) => b.priority - a.priority); // Sort by Priority descending
        logDebug("Priority 기준 정렬 후 데이터:", dataForTable);

        // 필터링 정보 표시 업데이트
        let filterSummary = "";
        if (projectFilter.length > 0) filterSummary += `**프로젝트:** ${projectFilterInput || projectFilter.join(', ')}`;
        if (epicFilter.length > 0) {
            if (filterSummary) filterSummary += " | ";
            filterSummary += `**Epic:** ${epicFilterInput || epicFilter.join(', ')}`;
        }
        if (statusFilter.length > 0) { // status 필터 요약 추가
             if (filterSummary) filterSummary += " | ";
             filterSummary += `**Status:** ${statusFilterInput || statusFilter.join(', ')}`;
        }


        if (filterSummary) {
             dv.paragraph(`--- **필터링 조건:** ${filterSummary} ---`);
        } else {
             dv.paragraph(`--- 전체 기간 활동 요약 (${startDateRange} ~ ${endDateRange}) ---`);
        }

        // 테이블 헤더 수정
        const header = `| 활동 (Activity) | Project | Epic | Status | Impact | Priority | 총 소요 시간 (Total) | 예상 시간 (Estimated) | 남은 시간 (Remaining) |
| :-------------- | :------ | :--- | :----- | :----- | :------- | :------------------- | :-------------------- | :-------------------- |`; // Status 열 추가

        // 테이블 행 생성 수정
        const rows = dataForTable.map(item => {
            const totalFormatted = formatMinutesToDHMS(item.totalDurationMinutes);
            const estimatedFormatted = formatMinutesToDHMS(item.estimatedMinutes);
            const remainingTimeToFormat = isNumber(item.remainingMinutes) && item.remainingMinutes < 0 ? 0 : item.remainingMinutes;
            const remainingFormatted = formatMinutesToDHMS(remainingTimeToFormat);
            const priorityFormatted = isFinite(item.priority) && item.priority > -Infinity ? item.priority.toFixed(2) : "-";
            const escapePipe = (str) => String(str).replace(/\|/g, "\\|");

            // Status 열 추가
            return `| ${escapePipe(item.activity)} | ${escapePipe(item.project)} | ${escapePipe(item.epic)} | ${escapePipe(item.status)} | ${escapePipe(item.impact)} | ${priorityFormatted} | ${totalFormatted} | ${estimatedFormatted} | ${remainingFormatted} |`;
        });

        // 테이블 합계 행 수정
        const totalActualFormatted = formatMinutesToDHMS(totalActualMinutesSum);
        const totalEstimatedFormatted = formatMinutesToDHMS(totalEstimatedMinutesSum);
        const totalRemainingFormatted = formatMinutesToDHMS(totalPositiveRemainingMinutes);
        const totalRow = `| **총 합계** | | | | | | **${totalActualFormatted}** | **${totalEstimatedFormatted}** | **${totalRemainingFormatted}** |`; // Status 열에 빈 칸 추가

        dv.paragraph(header + "\n" + rows.join("\n") + "\n" + totalRow);

    } else {
        // 필터링 결과 데이터가 없는 경우 메시지 업데이트
        let filterMsg = "";
        if (projectFilter.length > 0) filterMsg += `프로젝트(${projectFilterInput || projectFilter.join(', ')})`;
        if (epicFilter.length > 0) {
             if (filterMsg) filterMsg += " 및 ";
             filterMsg += `Epic(${epicFilterInput || epicFilter.join(', ')})`;
        }
         if (statusFilter.length > 0) { // status 필터 메시지 추가
             if (filterMsg) filterMsg += " 및 ";
             filterMsg += `Status(${statusFilterInput || statusFilter.join(', ')})`;
        }

        if (filterMsg) {
             dv.paragraph(`ℹ️ 선택된 ${filterMsg}에 해당하는 활동 로그를 찾지 못했습니다.`);
        } else {
             dv.paragraph("ℹ️ 유효한 활동 그룹이 없습니다 (Task와 매칭된 활동 없음).");
        }
    }
} else {
    dv.paragraph(`ℹ️ 지정된 기간(${startDateRange} ~ ${endDateRange}) 내 '${dailyNoteFolder}' 폴더에서 Task와 매칭되는 활동 로그를 찾지 못했습니다.`);
}

dv.paragraph("🏁 **스크립트 실행 종료**");
logDebug("스크립트 실행 종료.");
// --- SCRIPT END ---

```

```dataviewjs
// --- CONFIGURATION ---
// ⚠️ 중요: 아래 설정 값들을 자신의 Obsidian 환경에 맞게 정확히 수정해주세요!

// 📅 분석 기간 설정 (Date Range for Analysis)
const startDateRange = "2025-04-01"; // <--- !!! 시작 날짜 수정 !!!
const endDateRange = "2025-05-03";   // <--- !!! 종료 날짜 수정 !!!

// 📂 Task 파일들이 있는 폴더 경로 리스트 (List of Task Folder Paths)
const taskFolderPaths = [
    "02_Projects/Career/Grizzly Ridge/Task", // <--- 사용자 요청 경로 1
    "02_Projects/Career/Ratel2/Task",       // <--- 사용자 요청 경로 2
    "02_Projects/Career/Life Management Tool/Task", // <--- 사용자 요청 경로 3
    // "Tasks",
    // "02 - Areas/Action",
    // "Projects/My Project/Tasks"
];

// 📓 데일리 노트가 있는 폴더 경로 (Daily Notes Folder Path)
const dailyNoteFolder = "01_Daily/Daily"; // <--- !!! 자신의 데일리 노트 폴더 경로로 수정하세요 !!!

// ⭐ 동적 필터링: 아래 frontmatter 키를 사용하여 이 노트의 frontmatter에서 필터링합니다. ⭐
// --- 이 노트의 frontmatter에 다음 키를 추가하여 필터링하세요 ---
// project: "ProjectName1, ProjectName2"  (쉼표로 구분, 비워두면 모든 프로젝트 포함)
// epic: "EpicName1, EpicName2"        (쉼표로 구분, 비워두면 모든 Epic 포함)
// 예시:
// ---
// project: "Grizzly Ridge, Ratel2"
// epic: "gzr"
// ---
// --------------------------------------------------------------------

// --- DEBUGGING FLAGS ---
const enableVerboseLogging = true; // true로 설정하면 개발자 콘솔에 더 자세한 로그 출력

// --- CONSTANTS ---
const MINUTES_PER_HOUR = 60;
const MINUTES_PER_DAY = 24 * MINUTES_PER_HOUR; // 1일 = 24시간 기준

// --- FUNCTION DEFINITIONS ---

/**
 * 개발자 콘솔에 디버깅 메시지를 출력합니다.
 */
const logDebug = (message, data) => {
    if (enableVerboseLogging) {
        console.log(`[Dataview Debug] ${message}`, data !== undefined ? data : "");
    }
};

/**
 * 다양한 형식의 기간 문자열을 총 분(minute) 단위로 파싱합니다.
 */
const parseDurationToMinutes = (durationString) => {
    // ... (이전 코드와 동일 - no changes needed here) ...
    if (!durationString || typeof durationString !== 'string' || durationString.trim() === "" || durationString.trim() === "-") { return null; }
    durationString = durationString.trim(); let totalMinutes = 0;
    try {
        if (durationString.startsWith('P')) {
            let remainingString = durationString.substring(1); let timePart = remainingString.split('T')[1] || ''; let datePart = remainingString.split('T')[0];
            const dayMatch = datePart.match(/(\d+(\.\d+)?)D/); if (dayMatch) totalMinutes += parseFloat(dayMatch[1]) * MINUTES_PER_DAY;
            const hourMatch = timePart.match(/(\d+(\.\d+)?)H/); if (hourMatch) totalMinutes += parseFloat(hourMatch[1]) * MINUTES_PER_HOUR;
            const minuteMatch = timePart.match(/(\d+(\.\d+)?)M/); if (minuteMatch) totalMinutes += parseFloat(minuteMatch[1]);
            if (totalMinutes > 0 || dayMatch || hourMatch || minuteMatch) { return Math.round(totalMinutes); }
            logDebug(`parseDurationToMinutes (ISO): '${durationString}' 에서 유효 시간 단위 못찾음.`); totalMinutes = 0;
        }
        let combinedOrSimpleMinutes = 0; let matched = false;
        const parts = durationString.toLowerCase().match(/(\d+(\.\d+)?\s*[dhms])/g) || [];
        for (const part of parts) {
            const value = parseFloat(part); if (isNaN(value)) continue;
            if (part.includes('d')) { combinedOrSimpleMinutes += value * MINUTES_PER_DAY; matched = true;}
            else if (part.includes('h')) { combinedOrSimpleMinutes += value * MINUTES_PER_HOUR; matched = true;}
            else if (part.includes('m')) { combinedOrSimpleMinutes += value; matched = true; }
        }
         if (matched) { return Math.round(combinedOrSimpleMinutes); }
        const numberOnlyMatch = durationString.match(/^(\d+(\.\d+)?)$/);
        if (numberOnlyMatch) { totalMinutes = parseFloat(numberOnlyMatch[1]); return Math.round(totalMinutes); }
        logDebug(`parseDurationToMinutes: '${durationString}' 형식을 인식할 수 없음.`); return null;
    } catch (error) { dv.paragraph(`❌ **파싱 오류:** '${durationString}' 기간 파싱 중 오류 발생: ${error.message}`); logDebug("parseDurationToMinutes 오류 발생", error); return null; }
};

/**
 * 총 분(minute)을 "Xd Yh Zm" 형식의 문자열로 변환합니다.
 */
const formatMinutesToDHMS = (totalMinutes) => {
    // ... (이전 코드와 동일 - no changes needed here) ...
    if (totalMinutes === null || typeof totalMinutes !== 'number' || isNaN(totalMinutes)) { return "-"; }
    if (totalMinutes === 0) return "0m"; const sign = totalMinutes < 0 ? "-" : ""; let absMinutes = Math.abs(Math.round(totalMinutes));
    const days = Math.floor(absMinutes / MINUTES_PER_DAY); absMinutes %= MINUTES_PER_DAY;
    const hours = Math.floor(absMinutes / MINUTES_PER_HOUR); absMinutes %= MINUTES_PER_HOUR;
    const minutes = absMinutes; let result = "";
    if (days > 0) result += `${days}d `; if (hours > 0) result += `${hours}h `;
    if (minutes > 0 || (days === 0 && hours === 0)) { result += `${minutes}m`; }
    result = result.trim(); return result ? sign + result : "0m";
};

/**
 * YAML frontmatter 날짜 형식이 유효한지 확인합니다.
 */
const isValidDateString = (dateString) => {
    return /^\d{4}-\d{2}-\d{2}$/.test(dateString) && !isNaN(new Date(dateString));
};

/**
 * 숫자인지 확인하는 간단한 함수
 */
const isNumber = (value) => typeof value === 'number' && !isNaN(value);

/**
 * Frontmatter에서 필터 문자열을 파싱하여 소문자 배열로 반환합니다.
 */
const parseFilterString = (filterString) => {
    if (!filterString || typeof filterString !== 'string') {
        return [];
    }
    return filterString.split(',')          // 쉼표로 분리
                     .map(item => item.trim().toLowerCase()) // 공백 제거 및 소문자 변환
                     .filter(item => item !== ''); // 빈 항목 제거
};


// --- SCRIPT START ---
dv.paragraph("🚀 **Dataview Task Aggregator (Dynamic Filters)**");

// ⭐ Frontmatter에서 동적 필터 값 읽기 (키 이름 변경: project, epic) ⭐
const currentNote = dv.current(); // 현재 노트의 정보 가져오기
const projectFilterInput = currentNote?.project || ""; // frontmatter의 project 값 (없으면 빈 문자열)
const epicFilterInput = currentNote?.epic || "";     // frontmatter의 epic 값 (없으면 빈 문자열)

const projectFilter = parseFilterString(projectFilterInput);
const epicFilter = parseFilterString(epicFilterInput);

logDebug("스크립트 실행 시작", { startDateRange, endDateRange, taskFolderPaths, dailyNoteFolder });
logDebug("Frontmatter 필터 값:", { projectFilterInput, epicFilterInput });
logDebug("파싱된 필터:", { projectFilter, epicFilter });

// 날짜 범위 유효성 검사
if (!isValidDateString(startDateRange) || !isValidDateString(endDateRange)) {
    dv.paragraph(`❌ **설정 오류:** 시작 날짜(${startDateRange}) 또는 종료 날짜(${endDateRange}) 형식이 잘못되었습니다. "YYYY-MM-DD" 형식으로 입력해주세요.`);
    return;
}
const startDt = new Date(startDateRange);
const endDt = new Date(endDateRange);
endDt.setHours(23, 59, 59, 999);

if (startDt > endDt) {
    dv.paragraph(`❌ **설정 오류:** 시작 날짜(${startDateRange})가 종료 날짜(${endDateRange})보다 늦습니다.`);
    return;
}

// 1️⃣ Task 데이터 미리 가져오기 (Pre-fetch Task Data)
const taskData = {};
let totalTasksLoaded = 0;
let foldersSearched = 0;
let foldersFound = [];
let foldersNotFound = [];
let foldersFailed = [];

if (!Array.isArray(taskFolderPaths) || taskFolderPaths.length === 0) {
     dv.paragraph(`❌ **설정 오류:** 'taskFolderPaths'가 유효한 배열이 아니거나 비어 있습니다.`);
} else {
    dv.paragraph(`🔍 Task 폴더 검색 시작 (${taskFolderPaths.length}개 경로): ${taskFolderPaths.join(', ')}`);
    for (const folderPath of taskFolderPaths) {
        const currentFolderPath = typeof folderPath === 'string' ? folderPath.trim() : '';
        if (!currentFolderPath) { foldersFailed.push("(빈 경로)"); continue; }
        try {
            const taskPages = dv.pages(`"${currentFolderPath}"`);
            foldersSearched++;
            if (taskPages.length > 0) {
                foldersFound.push(currentFolderPath);
                for (const taskPage of taskPages) {
                    const taskName = taskPage.file.name;
                    const taskFilePath = taskPage.file.path;
                    const estimatedTimeRaw = taskPage.estimated;
                    const projectRaw = taskPage.project; // Task 노트의 frontmatter 키는 그대로 'project'
                    const epicRaw = taskPage.epic;       // Task 노트의 frontmatter 키는 그대로 'epic'
                    const impactRaw = taskPage.impact;

                    let impactNumber = null;
                    if (impactRaw !== undefined && impactRaw !== null) {
                        const parsedImpact = parseFloat(impactRaw);
                        if (!isNaN(parsedImpact)) { impactNumber = parsedImpact; }
                        else { logDebug(`'${taskName}' Task의 impact 값(${impactRaw})을 숫자로 파싱할 수 없음.`); }
                    }

                    const finalEstimatedRaw = (estimatedTimeRaw !== undefined && estimatedTimeRaw !== null && String(estimatedTimeRaw).trim() !== "") ? String(estimatedTimeRaw) : "-";
                    const finalProject = (projectRaw !== undefined && projectRaw !== null && String(projectRaw).trim() !== "") ? String(projectRaw) : "-";
                    const finalEpic = (epicRaw !== undefined && epicRaw !== null && String(epicRaw).trim() !== "") ? String(epicRaw) : "-";

                    if (taskName) {
                        if (!taskData.hasOwnProperty(taskName)) {
                            taskData[taskName] = {
                                estimatedRaw: finalEstimatedRaw, project: finalProject, epic: finalEpic,
                                impact: impactNumber, sourcePath: taskFilePath
                            };
                            totalTasksLoaded++;
                        }
                    }
                }
            } else { foldersNotFound.push(currentFolderPath); }
        } catch (e) {
            dv.paragraph(`❌ **폴더 오류:** '${currentFolderPath}' 폴더 처리 중 오류 발생: ${e.message}. (경로 및 접근 권한 확인)`);
            logDebug(`폴더 처리 오류 (${currentFolderPath})`, e); foldersFailed.push(currentFolderPath);
        }
    }
    dv.paragraph(`✅ Task 로딩 완료: ${foldersSearched}개 폴더 검색 시도. ${foldersFound.length}개 폴더에서 ${totalTasksLoaded}개 고유 Task 로드.`);
    if (foldersNotFound.length > 0) dv.paragraph(`ℹ️ 파일 없음: ${foldersNotFound.join(', ')} 폴더에서는 Task 파일을 찾지 못했습니다.`);
    if (foldersFailed.length > 0) dv.paragraph(`❌ 로딩 실패 폴더: ${foldersFailed.join(', ')}.`);
    if (totalTasksLoaded === 0 && foldersSearched > 0 && foldersFailed.length === 0) dv.paragraph(`⚠️ **Task 없음:** 지정된 폴더들에서 유효한 Task 파일을 찾을 수 없습니다.`);
    if (taskFolderPaths.length > 1) dv.paragraph("ℹ️ *참고: 동일 이름 Task는 리스트에서 먼저 검색된 폴더의 정보 사용.*");
    logDebug("최종 로드된 Task 데이터:", taskData);
}

// 2️⃣ 지정된 기간 내 데일리 노트 처리 (Process Daily Notes within Date Range)
dv.paragraph(`📄 데일리 노트 분석 시작: ${dailyNoteFolder} 폴더 (${startDateRange} ~ ${endDateRange})`);
logDebug("분석할 데일리 노트 폴더:", dailyNoteFolder);

const allActivities = [];
let dailyNotesProcessed = 0;
let dailyNotesFailed = 0;
let totalDurationSkippedTasks = 0;

try {
    const dailyPages = dv.pages(`"${dailyNoteFolder}"`);
    logDebug(`${dailyNoteFolder} 폴더에서 ${dailyPages.length}개의 파일을 찾았습니다.`);

    for (const page of dailyPages) {
        const fileName = page.file.name;
        if (/^\d{4}-\d{2}-\d{2}$/.test(fileName)) {
            const currentNoteDateStr = fileName;
            const currentNoteDt = new Date(currentNoteDateStr);

            if (!isNaN(currentNoteDt) && currentNoteDt >= startDt && currentNoteDt <= endDt) {
                dailyNotesProcessed++;
                let fileContent = null;
                try { fileContent = await dv.io.load(page.file.path); }
                catch (e) { dv.paragraph(`❌ **파일 읽기 오류:** ${page.file.link} 내용 읽기 실패: ${e.message}.`); logDebug(`데일리 노트 파일 읽기 실패: ${page.file.path}`, e); dailyNotesFailed++; continue; }

                let sectionContent = null;
                if (fileContent !== null) {
                    const plannerHeader = "## Day planner";
                    const headerStartIndex = fileContent.toLowerCase().indexOf(plannerHeader.toLowerCase());
                    if (headerStartIndex !== -1) {
                        const contentAfterHeaderStart = fileContent.substring(headerStartIndex + plannerHeader.length);
                        const nextHeaderMatch = contentAfterHeaderStart.match(/^\s*#{2,}\s+/m);
                        const contentEndIndex = nextHeaderMatch ? nextHeaderMatch.index : contentAfterHeaderStart.length;
                        sectionContent = contentAfterHeaderStart.substring(0, contentEndIndex).trim();
                    }
                }

                if (sectionContent !== null && sectionContent.length > 0) {
                    const lines = sectionContent.split('\n');
                    const lineRegex = /^\s*(?:[-*•]\s+)?(\d{1,2}:\d{2})\s*[-–~]\s*(\d{1,2}:\d{2})\s+(.*?)(?:\s+#.*)?$/;
                    let timeErrors = 0;

                    for (const line of lines) {
                        const trimmedLine = line.trim();
                        if (!trimmedLine || trimmedLine.startsWith('#')) continue;
                        logDebug(`처리 시도 라인 (${page.file.name}):`, trimmedLine);

                        const match = trimmedLine.match(lineRegex);
                        if (match) {
                            logDebug(`   -> 정규식 매칭 성공!`);
                            let startTimeStr = match[1].padStart(5, '0');
                            let endTimeStr = match[2].padStart(5, '0');
                            let activityDisplay = match[3].trim();
                            let potentialTaskName = activityDisplay;
                            let estimatedRawResult = "-"; let projectResult = "-"; let epicResult = "-";
                            let impactResult = null;

                            const linkMatch = activityDisplay.match(/^!?\[\[(.*?)\]\]$/);
                            if (linkMatch && linkMatch[1]) {
                                potentialTaskName = linkMatch[1].trim();
                                activityDisplay = linkMatch[0]; // Keep the link format for display
                            } else {
                                potentialTaskName = potentialTaskName
                                    .replace(/^\s*[\p{Emoji_Presentation}\p{Emoji}]\s*/u, '') // Remove leading emoji
                                    .replace(/^[ *_~]+|[ *_~]+$/g, '') // Trim markdown chars
                                    .replace(/[*_~]{1,3}(.*?)[*_~]{1,3}/g, '$1') // Remove surrounding markdown
                                    .trim();
                                activityDisplay = potentialTaskName; // Use cleaned name for display if not a link
                            }
                            logDebug(`   -> Task 이름 후보: '${potentialTaskName}'`);

                            let taskExists = false;
                            if (taskData.hasOwnProperty(potentialTaskName)) {
                                taskExists = true;
                                const taskInfo = taskData[potentialTaskName];
                                estimatedRawResult = taskInfo.estimatedRaw; projectResult = taskInfo.project;
                                epicResult = taskInfo.epic; impactResult = taskInfo.impact;
                                logDebug(`   -> Task 매칭됨: '${potentialTaskName}'`);
                            } else { logDebug(`   -> Task 매칭 안됨: '${potentialTaskName}'`); }

                            let durationMinutes = 0;
                             try {
                                const start = new Date(`${currentNoteDateStr}T${startTimeStr}:00`);
                                const end = new Date(`${currentNoteDateStr}T${endTimeStr}:00`);
                                if (isNaN(start.getTime()) || isNaN(end.getTime())) { logDebug(`   -> 시간 변환 오류`); timeErrors++; continue; }
                                if (start >= end) {
                                     logDebug(`   -> 종료 시간이 시작 시간보다 빠르거나 같음. 날짜 조정 시도.`);
                                     end.setDate(end.getDate() + 1);
                                     if (start >= end) { logDebug(`   -> 날짜 조정 후에도 시간 순서 오류. 건너뜀.`); timeErrors++; continue; }
                                }
                                durationMinutes = (end - start) / (1000 * 60);
                                logDebug(`   -> 계산된 시간: ${durationMinutes.toFixed(2)}분`);
                                if (durationMinutes <= 0) continue;
                            } catch (e) { dv.paragraph(`❌ **시간 처리 오류:** ${page.file.link}의 '${trimmedLine}' 처리 중 오류: ${e.message}`); logDebug(`시간 처리 예외 발생 (${page.file.name}): ${trimmedLine}`, e); timeErrors++; continue; }

                            if (taskExists) {
                                if (!activityDisplay) activityDisplay = "(설명 없음)";
                                allActivities.push({
                                    activityDisplay, duration: Math.round(durationMinutes),
                                    estimatedRaw: estimatedRawResult, project: projectResult, epic: epicResult,
                                    impact: impactResult
                                });
                                logDebug(`   => 활동 추가됨 (Task 존재): '${activityDisplay}', duration: ${Math.round(durationMinutes)}`);
                            } else {
                                totalDurationSkippedTasks += durationMinutes;
                                logDebug(`   => 활동 건너뜀 (Task 없음): '${activityDisplay}', 시간: ${durationMinutes.toFixed(2)}분`);
                            }
                        } else { logDebug("   -> 정규식 매칭 실패 (처리 안함)"); }
                    } // End of line loop
                     if (timeErrors > 0) dv.paragraph(`⚠️ ${page.file.link} 처리 중 ${timeErrors}개의 시간 관련 오류/경고 발생.`);
                }
            }
        }
    } // End of page loop

    dv.paragraph(`✅ 데일리 노트 처리 완료: 총 ${dailyNotesProcessed}개 파일 분석 완료. ${dailyNotesFailed}개 파일 읽기 실패.`);
    if (totalDurationSkippedTasks > 0) {
         dv.paragraph(`ℹ️ **참고:** Task 파일이 없어 집계에서 제외된 활동들의 총 시간은 약 ${formatMinutesToDHMS(totalDurationSkippedTasks)} 입니다.`);
    }

} catch (e) {
    dv.paragraph(`❌ **폴더 처리 오류:** 데일리 노트 폴더('${dailyNoteFolder}') 처리 중 오류 발생: ${e.message}.`);
    logDebug(`데일리 노트 폴더 처리 오류`, e);
}


// 3️⃣ 최종 결과 집계 및 출력 (Aggregate Final Results and Render)
if (allActivities.length > 0) {
    logDebug("최종 결과 집계 시작. Task와 매칭된 활동 항목 수:", allActivities.length);

    const grouped = allActivities.reduce((acc, { activityDisplay, duration, estimatedRaw, project, epic, impact }) => {
        if (!acc[activityDisplay]) {
            acc[activityDisplay] = { totalDuration: 0, estimatedRaw: estimatedRaw, project: project, epic: epic, impact: impact };
        }
        // Use the first non-empty value found for metadata
        if (!acc[activityDisplay].estimatedRaw || acc[activityDisplay].estimatedRaw === "-") acc[activityDisplay].estimatedRaw = estimatedRaw;
        if (!acc[activityDisplay].project || acc[activityDisplay].project === "-") acc[activityDisplay].project = project;
        if (!acc[activityDisplay].epic || acc[activityDisplay].epic === "-") acc[activityDisplay].epic = epic;
        if (!isNumber(acc[activityDisplay].impact) && isNumber(impact)) acc[activityDisplay].impact = impact;
        acc[activityDisplay].totalDuration += duration;
        return acc;
    }, {});
    logDebug("최종 활동별 집계 결과 (Task 존재하는 것만):", grouped);

    // ⭐ 프로젝트 및 Epic 필터링 적용 (Using parsed frontmatter filters) ⭐
    // projectFilter and epicFilter are already lowercase arrays from parseFilterString
    const filteredGroupedEntries = Object.entries(grouped).filter(([activity, data]) => {
        const projectMatch = projectFilter.length === 0 || projectFilter.includes(data.project.toLowerCase());
        const epicMatch = epicFilter.length === 0 || epicFilter.includes(data.epic.toLowerCase());
        return projectMatch && epicMatch; // Must match both filters if they are active
    });
    logDebug("프로젝트/Epic 필터링 후 항목 수:", filteredGroupedEntries.length);

    if (filteredGroupedEntries.length > 0) {
        let totalPositiveRemainingMinutes = 0;
        let totalActualMinutesSum = 0;
        let totalEstimatedMinutesSum = 0;

        const dataForTable = filteredGroupedEntries.map(([activity, data]) => {
            const estimatedMinutes = parseDurationToMinutes(data.estimatedRaw);
            const impact = data.impact;
            let priority = -Infinity;
            if (isNumber(impact) && isNumber(estimatedMinutes) && estimatedMinutes > 0) {
                priority = impact / estimatedMinutes;
            }

            let remainingMinutes = null;
            if (isNumber(estimatedMinutes)) {
                remainingMinutes = estimatedMinutes - data.totalDuration;
                if (remainingMinutes > 0) {
                    totalPositiveRemainingMinutes += remainingMinutes;
                }
                totalEstimatedMinutesSum += estimatedMinutes;
            }
            totalActualMinutesSum += data.totalDuration;

            return {
                activity, project: data.project, epic: data.epic,
                impact: isNumber(impact) ? impact : "-",
                totalDurationMinutes: data.totalDuration,
                estimatedMinutes: estimatedMinutes,
                priority: priority,
                remainingMinutes: remainingMinutes
            };
        });

        dataForTable.sort((a, b) => b.priority - a.priority); // Sort by Priority descending
        logDebug("Priority 기준 정렬 후 데이터:", dataForTable);

        // 필터링 정보 표시 업데이트
        let filterSummary = "";
        // Use the original input strings for display if available, otherwise join the parsed array
        if (projectFilter.length > 0) filterSummary += `**프로젝트:** ${projectFilterInput || projectFilter.join(', ')}`;
        if (epicFilter.length > 0) {
            if (filterSummary) filterSummary += " | "; // 구분자 추가
            filterSummary += `**Epic:** ${epicFilterInput || epicFilter.join(', ')}`;
        }

        if (filterSummary) {
             dv.paragraph(`--- **필터링 조건:** ${filterSummary} ---`);
        } else {
             dv.paragraph(`--- 전체 기간 활동 요약 (${startDateRange} ~ ${endDateRange}) ---`);
        }

        const header = `| 활동 (Activity) | Project | Epic | Impact | Priority | 총 소요 시간 (Total) | 예상 시간 (Estimated) | 남은 시간 (Remaining) |
| :-------------- | :------ | :--- | :----- | :------- | :------------------- | :-------------------- | :-------------------- |`;

        const rows = dataForTable.map(item => {
            const totalFormatted = formatMinutesToDHMS(item.totalDurationMinutes);
            const estimatedFormatted = formatMinutesToDHMS(item.estimatedMinutes);
            // Only show positive remaining time or 0m in the summary column
            const remainingTimeToFormat = isNumber(item.remainingMinutes) && item.remainingMinutes < 0 ? 0 : item.remainingMinutes;
            const remainingFormatted = formatMinutesToDHMS(remainingTimeToFormat);
            const priorityFormatted = isFinite(item.priority) && item.priority > -Infinity ? item.priority.toFixed(2) : "-";
            const escapePipe = (str) => String(str).replace(/\|/g, "\\|"); // Escape pipe characters for Markdown table

            return `| ${escapePipe(item.activity)} | ${escapePipe(item.project)} | ${escapePipe(item.epic)} | ${escapePipe(item.impact)} | ${priorityFormatted} | ${totalFormatted} | ${estimatedFormatted} | ${remainingFormatted} |`;
        });

        const totalActualFormatted = formatMinutesToDHMS(totalActualMinutesSum);
        const totalEstimatedFormatted = formatMinutesToDHMS(totalEstimatedMinutesSum);
        const totalRemainingFormatted = formatMinutesToDHMS(totalPositiveRemainingMinutes); // Sum of only positive remaining times
        const totalRow = `| **총 합계** | | | | | **${totalActualFormatted}** | **${totalEstimatedFormatted}** | **${totalRemainingFormatted}** |`;

        dv.paragraph(header + "\n" + rows.join("\n") + "\n" + totalRow);

    } else {
        // 필터링 결과 데이터가 없는 경우 메시지 업데이트
        let filterMsg = "";
        if (projectFilter.length > 0) filterMsg += `프로젝트(${projectFilterInput || projectFilter.join(', ')})`;
        if (epicFilter.length > 0) {
             if (filterMsg) filterMsg += " 및 ";
             filterMsg += `Epic(${epicFilterInput || epicFilter.join(', ')})`;
        }
        if (filterMsg) {
             dv.paragraph(`ℹ️ 선택된 ${filterMsg}에 해당하는 활동 로그를 찾지 못했습니다.`);
        } else {
             // This case should ideally not happen if allActivities.length > 0,
             // but included for completeness. It means grouping/filtering removed everything.
             dv.paragraph("ℹ️ 유효한 활동 그룹이 없습니다 (Task와 매칭된 활동 없음).");
        }
    }
} else {
    dv.paragraph(`ℹ️ 지정된 기간(${startDateRange} ~ ${endDateRange}) 내 '${dailyNoteFolder}' 폴더에서 Task와 매칭되는 활동 로그를 찾지 못했습니다.`);
}

dv.paragraph("🏁 **스크립트 실행 종료**");
logDebug("스크립트 실행 종료.");
// --- SCRIPT END ---


```