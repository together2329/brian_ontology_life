```dataviewjs
// --- CONFIGURATION ---
// ⚠️ 중요: 아래 설정 값들을 자신의 Obsidian 환경에 맞게 정확히 수정해주세요!

// 📅 분석 기간 설정 (Date Range for Analysis)
const startDateRange = "2025-05-03"; // <--- !!! 시작 날짜 수정 !!!
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

// ⭐ 프로젝트 필터링 (Project Filtering)
// 특정 프로젝트만 보려면 배열 안에 프로젝트 이름을 넣으세요 (대소문자 구분 없음).
// 예: ["Grizzly Ridge", "Ratel2"]
// 빈 배열 [] 로 두면 모든 프로젝트를 포함합니다.
const projectFilter = []; // <--- !!! 필터링할 프로젝트 이름 추가 (선택 사항) !!!

// ⭐ Epic 필터링 (Epic Filtering)
// 특정 Epic만 보려면 배열 안에 Epic 이름을 넣으세요 (대소문자 구분 없음).
// 예: ["gzr", "rtl"]
// 빈 배열 [] 로 두면 모든 Epic을 포함합니다.
const epicFilter = []; // <--- !!! 필터링할 Epic 이름 추가 (선택 사항) !!!

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


// --- SCRIPT START ---
dv.paragraph("🚀 **Dataview Task Aggregator (Add Epic Filter)**"); // Title updated
logDebug("스크립트 실행 시작", { startDateRange, endDateRange, taskFolderPaths, dailyNoteFolder, projectFilter, epicFilter }); // epicFilter 로그 추가

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
                    const projectRaw = taskPage.project;
                    const epicRaw = taskPage.epic;
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
                                activityDisplay = linkMatch[0];
                            } else {
                                potentialTaskName = potentialTaskName
                                    .replace(/^\s*[\p{Emoji_Presentation}\p{Emoji}]\s*/u, '')
                                    .replace(/^[ *_~]+|[ *_~]+$/g, '')
                                    .replace(/[*_~]{1,3}(.*?)[*_~]{1,3}/g, '$1')
                                    .trim();
                                activityDisplay = potentialTaskName;
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
        if (!acc[activityDisplay].estimatedRaw || acc[activityDisplay].estimatedRaw === "-") acc[activityDisplay].estimatedRaw = estimatedRaw;
        if (!acc[activityDisplay].project || acc[activityDisplay].project === "-") acc[activityDisplay].project = project;
        if (!acc[activityDisplay].epic || acc[activityDisplay].epic === "-") acc[activityDisplay].epic = epic;
        if (!isNumber(acc[activityDisplay].impact) && isNumber(impact)) acc[activityDisplay].impact = impact;
        acc[activityDisplay].totalDuration += duration;
        return acc;
    }, {});
    logDebug("최종 활동별 집계 결과 (Task 존재하는 것만):", grouped);

    // ⭐ 프로젝트 및 Epic 필터링 적용 ⭐
    const projectFilterLower = projectFilter.map(p => p.toLowerCase());
    const epicFilterLower = epicFilter.map(e => e.toLowerCase()); // Epic 필터 소문자 변환

    const filteredGroupedEntries = Object.entries(grouped).filter(([activity, data]) => {
        const projectMatch = projectFilterLower.length === 0 || projectFilterLower.includes(data.project.toLowerCase());
        const epicMatch = epicFilterLower.length === 0 || epicFilterLower.includes(data.epic.toLowerCase()); // Epic 필터 조건 추가
        return projectMatch && epicMatch; // Project와 Epic 모두 만족해야 함
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

        dataForTable.sort((a, b) => b.priority - a.priority);
        logDebug("Priority 기준 정렬 후 데이터:", dataForTable);

        // 필터링 정보 표시 업데이트
        let filterSummary = "";
        if (projectFilter.length > 0) filterSummary += `**프로젝트:** ${projectFilter.join(', ')}`;
        if (epicFilter.length > 0) {
            if (filterSummary) filterSummary += " | "; // 구분자 추가
            filterSummary += `**Epic:** ${epicFilter.join(', ')}`;
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
            const remainingTimeToFormat = isNumber(item.remainingMinutes) && item.remainingMinutes < 0 ? 0 : item.remainingMinutes;
            const remainingFormatted = formatMinutesToDHMS(remainingTimeToFormat);
            const priorityFormatted = isFinite(item.priority) && item.priority > -Infinity ? item.priority.toFixed(2) : "-";
            const escapePipe = (str) => String(str).replace(/\|/g, "\\|");

            return `| ${escapePipe(item.activity)} | ${escapePipe(item.project)} | ${escapePipe(item.epic)} | ${escapePipe(item.impact)} | ${priorityFormatted} | ${totalFormatted} | ${estimatedFormatted} | ${remainingFormatted} |`;
        });

        const totalActualFormatted = formatMinutesToDHMS(totalActualMinutesSum);
        const totalEstimatedFormatted = formatMinutesToDHMS(totalEstimatedMinutesSum);
        const totalRemainingFormatted = formatMinutesToDHMS(totalPositiveRemainingMinutes);
        const totalRow = `| **총 합계** | | | | | **${totalActualFormatted}** | **${totalEstimatedFormatted}** | **${totalRemainingFormatted}** |`;

        dv.paragraph(header + "\n" + rows.join("\n") + "\n" + totalRow);

    } else {
         // 필터링 결과 데이터가 없는 경우 메시지 업데이트
         let filterMsg = "";
         if (projectFilter.length > 0) filterMsg += `프로젝트(${projectFilter.join(', ')})`;
         if (epicFilter.length > 0) {
             if (filterMsg) filterMsg += " 및 ";
             filterMsg += `Epic(${epicFilter.join(', ')})`;
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
const endDateRange = "2025-05-02";   // <--- !!! 종료 날짜 수정 !!!

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

// ⭐ 프로젝트 필터링 (Project Filtering)
// 특정 프로젝트만 보려면 배열 안에 프로젝트 이름을 넣으세요 (대소문자 구분 없음).
// 예: ["Grizzly Ridge", "Ratel2"]
// 빈 배열 [] 로 두면 모든 프로젝트를 포함합니다.
const projectFilter = ["grizzlyridge"]; // <--- !!! 필터링할 프로젝트 이름 추가 (선택 사항) !!!

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


// --- SCRIPT START ---
dv.paragraph("🚀 **Dataview Task Aggregator (Add Total Time Sums)**"); // Title updated
logDebug("스크립트 실행 시작", { startDateRange, endDateRange, taskFolderPaths, dailyNoteFolder, projectFilter });

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
                    const projectRaw = taskPage.project;
                    const epicRaw = taskPage.epic;
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
                                activityDisplay = linkMatch[0];
                            } else {
                                potentialTaskName = potentialTaskName
                                    .replace(/^\s*[\p{Emoji_Presentation}\p{Emoji}]\s*/u, '')
                                    .replace(/^[ *_~]+|[ *_~]+$/g, '')
                                    .replace(/[*_~]{1,3}(.*?)[*_~]{1,3}/g, '$1')
                                    .trim();
                                activityDisplay = potentialTaskName;
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
        if (!acc[activityDisplay].estimatedRaw || acc[activityDisplay].estimatedRaw === "-") acc[activityDisplay].estimatedRaw = estimatedRaw;
        if (!acc[activityDisplay].project || acc[activityDisplay].project === "-") acc[activityDisplay].project = project;
        if (!acc[activityDisplay].epic || acc[activityDisplay].epic === "-") acc[activityDisplay].epic = epic;
        if (!isNumber(acc[activityDisplay].impact) && isNumber(impact)) acc[activityDisplay].impact = impact;
        acc[activityDisplay].totalDuration += duration;
        return acc;
    }, {});
    logDebug("최종 활동별 집계 결과 (Task 존재하는 것만):", grouped);

    const projectFilterLower = projectFilter.map(p => p.toLowerCase());
    const filteredGroupedEntries = Object.entries(grouped).filter(([activity, data]) => {
        if (projectFilterLower.length === 0) return true;
        return projectFilterLower.includes(data.project.toLowerCase());
    });
    logDebug("프로젝트 필터링 후 항목 수:", filteredGroupedEntries.length);

    if (filteredGroupedEntries.length > 0) {
        let totalPositiveRemainingMinutes = 0; // 총 남은 시간 합계 (양수만)
        let totalActualMinutesSum = 0;       // ⭐ 총 소요 시간 합계
        let totalEstimatedMinutesSum = 0;    // ⭐ 총 예상 시간 합계

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
                // ⭐ 예상 시간 합계 누적
                totalEstimatedMinutesSum += estimatedMinutes;
            }
            // ⭐ 소요 시간 합계 누적
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

        dataForTable.sort((a, b) => b.priority - a.priority);
        logDebug("Priority 기준 정렬 후 데이터:", dataForTable);

        if (projectFilter.length > 0) {
             dv.paragraph(`--- **필터링된 프로젝트:** ${projectFilter.join(', ')} ---`);
        } else {
             dv.paragraph(`--- 전체 기간 활동 요약 (${startDateRange} ~ ${endDateRange}) ---`);
        }

        const header = `| 활동 (Activity) | Project | Epic | Impact | Priority | 총 소요 시간 (Total) | 예상 시간 (Estimated) | 남은 시간 (Remaining) |
| :-------------- | :------ | :--- | :----- | :------- | :------------------- | :-------------------- | :-------------------- |`;

        const rows = dataForTable.map(item => {
            const totalFormatted = formatMinutesToDHMS(item.totalDurationMinutes);
            const estimatedFormatted = formatMinutesToDHMS(item.estimatedMinutes);
            const remainingTimeToFormat = isNumber(item.remainingMinutes) && item.remainingMinutes < 0 ? 0 : item.remainingMinutes;
            const remainingFormatted = formatMinutesToDHMS(remainingTimeToFormat);
            const priorityFormatted = isFinite(item.priority) && item.priority > -Infinity ? item.priority.toFixed(2) : "-";
            const escapePipe = (str) => String(str).replace(/\|/g, "\\|");

            return `| ${escapePipe(item.activity)} | ${escapePipe(item.project)} | ${escapePipe(item.epic)} | ${escapePipe(item.impact)} | ${priorityFormatted} | ${totalFormatted} | ${estimatedFormatted} | ${remainingFormatted} |`;
        });

        // ⭐ 총 합계 행 생성 (소요 시간, 예상 시간, 남은 시간)
        const totalActualFormatted = formatMinutesToDHMS(totalActualMinutesSum);
        const totalEstimatedFormatted = formatMinutesToDHMS(totalEstimatedMinutesSum);
        const totalRemainingFormatted = formatMinutesToDHMS(totalPositiveRemainingMinutes);
        const totalRow = `| **총 합계** | | | | | **${totalActualFormatted}** | **${totalEstimatedFormatted}** | **${totalRemainingFormatted}** |`; // 합계 행

        dv.paragraph(header + "\n" + rows.join("\n") + "\n" + totalRow); // 테이블 끝에 합계 행 추가

    } else {
         if (projectFilter.length > 0) {
             dv.paragraph(`ℹ️ 선택된 프로젝트(${projectFilter.join(', ')})에 해당하는 활동 로그를 찾지 못했습니다.`);
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
const endDateRange = "2025-05-02";   // <--- !!! 종료 날짜 수정 !!!

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

// ⭐ 프로젝트 필터링 (Project Filtering)
// 특정 프로젝트만 보려면 배열 안에 프로젝트 이름을 넣으세요 (대소문자 구분 없음).
// 예: ["Grizzly Ridge", "Ratel2"]
// 빈 배열 [] 로 두면 모든 프로젝트를 포함합니다.
const projectFilter = ["grizzlyridge"]; // <--- !!! 필터링할 프로젝트 이름 추가 (선택 사항) !!!

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


// --- SCRIPT START ---
dv.paragraph("🚀 **Dataview Task Aggregator (Remaining Time Sum & Zero Clamp)**"); // Title updated
logDebug("스크립트 실행 시작", { startDateRange, endDateRange, taskFolderPaths, dailyNoteFolder, projectFilter });

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
                    const projectRaw = taskPage.project;
                    const epicRaw = taskPage.epic;
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
                                activityDisplay = linkMatch[0];
                            } else {
                                potentialTaskName = potentialTaskName
                                    .replace(/^\s*[\p{Emoji_Presentation}\p{Emoji}]\s*/u, '')
                                    .replace(/^[ *_~]+|[ *_~]+$/g, '')
                                    .replace(/[*_~]{1,3}(.*?)[*_~]{1,3}/g, '$1')
                                    .trim();
                                activityDisplay = potentialTaskName;
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
        if (!acc[activityDisplay].estimatedRaw || acc[activityDisplay].estimatedRaw === "-") acc[activityDisplay].estimatedRaw = estimatedRaw;
        if (!acc[activityDisplay].project || acc[activityDisplay].project === "-") acc[activityDisplay].project = project;
        if (!acc[activityDisplay].epic || acc[activityDisplay].epic === "-") acc[activityDisplay].epic = epic;
        if (!isNumber(acc[activityDisplay].impact) && isNumber(impact)) acc[activityDisplay].impact = impact;
        acc[activityDisplay].totalDuration += duration;
        return acc;
    }, {});
    logDebug("최종 활동별 집계 결과 (Task 존재하는 것만):", grouped);

    const projectFilterLower = projectFilter.map(p => p.toLowerCase());
    const filteredGroupedEntries = Object.entries(grouped).filter(([activity, data]) => {
        if (projectFilterLower.length === 0) return true;
        return projectFilterLower.includes(data.project.toLowerCase());
    });
    logDebug("프로젝트 필터링 후 항목 수:", filteredGroupedEntries.length);

    if (filteredGroupedEntries.length > 0) {
        let totalPositiveRemainingMinutes = 0; // ⭐ 총 남은 시간 합계 변수

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
                // ⭐ 남은 시간이 양수일 경우 합계에 더함
                if (remainingMinutes > 0) {
                    totalPositiveRemainingMinutes += remainingMinutes;
                }
            }

            return {
                activity, project: data.project, epic: data.epic,
                impact: isNumber(impact) ? impact : "-",
                totalDurationMinutes: data.totalDuration,
                estimatedMinutes: estimatedMinutes,
                priority: priority,
                // ⭐ 계산된 remainingMinutes 저장 (음수일 수도 있음)
                remainingMinutes: remainingMinutes
            };
        });

        dataForTable.sort((a, b) => b.priority - a.priority);
        logDebug("Priority 기준 정렬 후 데이터:", dataForTable);

        if (projectFilter.length > 0) {
             dv.paragraph(`--- **필터링된 프로젝트:** ${projectFilter.join(', ')} ---`);
        } else {
             dv.paragraph(`--- 전체 기간 활동 요약 (${startDateRange} ~ ${endDateRange}) ---`);
        }

        const header = `| 활동 (Activity) | Project | Epic | Impact | Priority | 총 소요 시간 (Total) | 예상 시간 (Estimated) | 남은 시간 (Remaining) |
| :-------------- | :------ | :--- | :----- | :------- | :------------------- | :-------------------- | :-------------------- |`;

        const rows = dataForTable.map(item => {
            const totalFormatted = formatMinutesToDHMS(item.totalDurationMinutes);
            const estimatedFormatted = formatMinutesToDHMS(item.estimatedMinutes);
            // ⭐ 남은 시간이 음수면 0으로 처리하여 포맷팅
            const remainingTimeToFormat = isNumber(item.remainingMinutes) && item.remainingMinutes < 0 ? 0 : item.remainingMinutes;
            const remainingFormatted = formatMinutesToDHMS(remainingTimeToFormat);
            const priorityFormatted = isFinite(item.priority) && item.priority > -Infinity ? item.priority.toFixed(2) : "-";
            const escapePipe = (str) => String(str).replace(/\|/g, "\\|");

            return `| ${escapePipe(item.activity)} | ${escapePipe(item.project)} | ${escapePipe(item.epic)} | ${escapePipe(item.impact)} | ${priorityFormatted} | ${totalFormatted} | ${estimatedFormatted} | ${remainingFormatted} |`;
        });

        // ⭐ 총 남은 시간 행 추가
        const totalRemainingFormatted = formatMinutesToDHMS(totalPositiveRemainingMinutes);
        const totalRow = `| **총 남은 시간 합계** | | | | | | | **${totalRemainingFormatted}** |`; // 합계 행

        dv.paragraph(header + "\n" + rows.join("\n") + "\n" + totalRow); // 테이블 끝에 합계 행 추가

    } else {
         if (projectFilter.length > 0) {
             dv.paragraph(`ℹ️ 선택된 프로젝트(${projectFilter.join(', ')})에 해당하는 활동 로그를 찾지 못했습니다.`);
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
const endDateRange = "2025-05-02";   // <--- !!! 종료 날짜 수정 !!!

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

// ⭐ 프로젝트 필터링 (Project Filtering)
// 특정 프로젝트만 보려면 배열 안에 프로젝트 이름을 넣으세요 (대소문자 구분 없음).
// 예: ["Grizzly Ridge", "Ratel2"]
// 빈 배열 [] 로 두면 모든 프로젝트를 포함합니다.
const projectFilter = ["grizzlyridge"]; // <--- !!! 필터링할 프로젝트 이름 추가 (선택 사항) !!!

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


// --- SCRIPT START ---
dv.paragraph("🚀 **Dataview Task Aggregator (Project Filter Added)**"); // Title updated
logDebug("스크립트 실행 시작", { startDateRange, endDateRange, taskFolderPaths, dailyNoteFolder, projectFilter });

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
                    const projectRaw = taskPage.project;
                    const epicRaw = taskPage.epic;
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
                                activityDisplay = linkMatch[0];
                                logDebug(`   -> 링크 활동명. Task 이름: '${potentialTaskName}'`);
                            } else {
                                potentialTaskName = potentialTaskName
                                    .replace(/^\s*[\p{Emoji_Presentation}\p{Emoji}]\s*/u, '')
                                    .replace(/^[ *_~]+|[ *_~]+$/g, '')
                                    .replace(/[*_~]{1,3}(.*?)[*_~]{1,3}/g, '$1')
                                    .trim();
                                activityDisplay = potentialTaskName;
                                logDebug(`   -> 일반 텍스트 활동명. Task 이름: '${potentialTaskName}'`);
                            }

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
        // 첫 번째 항목의 메타데이터 유지 (덮어쓰지 않음)
        if (!acc[activityDisplay].estimatedRaw || acc[activityDisplay].estimatedRaw === "-") acc[activityDisplay].estimatedRaw = estimatedRaw;
        if (!acc[activityDisplay].project || acc[activityDisplay].project === "-") acc[activityDisplay].project = project;
        if (!acc[activityDisplay].epic || acc[activityDisplay].epic === "-") acc[activityDisplay].epic = epic;
        if (!isNumber(acc[activityDisplay].impact) && isNumber(impact)) acc[activityDisplay].impact = impact;

        acc[activityDisplay].totalDuration += duration;
        return acc;
    }, {});
    logDebug("최종 활동별 집계 결과 (Task 존재하는 것만):", grouped);

    // ⭐ 프로젝트 필터링 적용 ⭐
    const projectFilterLower = projectFilter.map(p => p.toLowerCase()); // 비교를 위해 소문자로 변환
    const filteredGroupedEntries = Object.entries(grouped).filter(([activity, data]) => {
        // projectFilter 배열이 비어있으면 모든 항목 포함
        if (projectFilterLower.length === 0) {
            return true;
        }
        // data.project 값이 projectFilter 배열에 포함되어 있는지 확인 (대소문자 무시)
        return projectFilterLower.includes(data.project.toLowerCase());
    });
    logDebug("프로젝트 필터링 후 항목 수:", filteredGroupedEntries.length);

    if (filteredGroupedEntries.length > 0) {
        // 필터링된 데이터로 테이블 생성 및 정렬
        const dataForTable = filteredGroupedEntries.map(([activity, data]) => {
            const estimatedMinutes = parseDurationToMinutes(data.estimatedRaw);
            const impact = data.impact;
            let priority = -Infinity;

            if (isNumber(impact) && isNumber(estimatedMinutes) && estimatedMinutes > 0) {
                priority = impact / estimatedMinutes;
            }

            return {
                activity, project: data.project, epic: data.epic,
                impact: isNumber(impact) ? impact : "-",
                totalDurationMinutes: data.totalDuration,
                estimatedMinutes: estimatedMinutes,
                priority: priority
            };
        });

        dataForTable.sort((a, b) => b.priority - a.priority);
        logDebug("Priority 기준 정렬 후 데이터:", dataForTable);

        // 필터링 정보 표시
        if (projectFilter.length > 0) {
             dv.paragraph(`--- **필터링된 프로젝트:** ${projectFilter.join(', ')} ---`);
        } else {
             dv.paragraph(`--- 전체 기간 활동 요약 (${startDateRange} ~ ${endDateRange}) ---`);
        }

        const header = `| 활동 (Activity) | Project | Epic | Impact | Priority | 총 소요 시간 (Total) | 예상 시간 (Estimated) | 남은 시간 (Remaining) |
| :-------------- | :------ | :--- | :----- | :------- | :------------------- | :-------------------- | :-------------------- |`;

        const rows = dataForTable.map(item => {
            let remainingMinutes = null;
            if (isNumber(item.estimatedMinutes)) {
                remainingMinutes = item.estimatedMinutes - item.totalDurationMinutes;
            }
            const totalFormatted = formatMinutesToDHMS(item.totalDurationMinutes);
            const estimatedFormatted = formatMinutesToDHMS(item.estimatedMinutes);
            const remainingFormatted = formatMinutesToDHMS(remainingMinutes);
            const priorityFormatted = isFinite(item.priority) && item.priority > -Infinity ? item.priority.toFixed(2) : "-";
            const escapePipe = (str) => String(str).replace(/\|/g, "\\|");

            return `| ${escapePipe(item.activity)} | ${escapePipe(item.project)} | ${escapePipe(item.epic)} | ${escapePipe(item.impact)} | ${priorityFormatted} | ${totalFormatted} | ${estimatedFormatted} | ${remainingFormatted} |`;
        });

        dv.paragraph(header + "\n" + rows.join("\n"));
    } else {
         // 필터링 결과 데이터가 없는 경우 메시지
         if (projectFilter.length > 0) {
             dv.paragraph(`ℹ️ 선택된 프로젝트(${projectFilter.join(', ')})에 해당하는 활동 로그를 찾지 못했습니다.`);
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
const startDateRange = "2025-04-20"; // <--- !!! 시작 날짜 수정 !!!
const endDateRange = "2025-05-02";   // <--- !!! 종료 날짜 수정 !!!

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
 * @param {string} durationString - 파싱할 기간 문자열
 * @returns {number|null} 총 분(minute) 또는 파싱 실패 시 null
 */
const parseDurationToMinutes = (durationString) => {
    if (!durationString || typeof durationString !== 'string' || durationString.trim() === "" || durationString.trim() === "-") {
        return null;
    }
    durationString = durationString.trim();
    let totalMinutes = 0;
    try {
        // 1. ISO 8601 Duration 형식 (예: P1DT2H30M, PT10H)
        if (durationString.startsWith('P')) {
            let remainingString = durationString.substring(1);
            let timePart = remainingString.split('T')[1] || '';
            let datePart = remainingString.split('T')[0];
            const dayMatch = datePart.match(/(\d+(\.\d+)?)D/);
            if (dayMatch) totalMinutes += parseFloat(dayMatch[1]) * MINUTES_PER_DAY;
            const hourMatch = timePart.match(/(\d+(\.\d+)?)H/);
            if (hourMatch) totalMinutes += parseFloat(hourMatch[1]) * MINUTES_PER_HOUR;
            const minuteMatch = timePart.match(/(\d+(\.\d+)?)M/);
            if (minuteMatch) totalMinutes += parseFloat(minuteMatch[1]);
            if (totalMinutes > 0 || dayMatch || hourMatch || minuteMatch) {
                 // logDebug(`parseDurationToMinutes (ISO): '${durationString}' -> ${Math.round(totalMinutes)}분`);
                 return Math.round(totalMinutes);
            }
            logDebug(`parseDurationToMinutes (ISO): '${durationString}' 에서 유효 시간 단위 못찾음. 다른 형식 시도.`);
            totalMinutes = 0;
        }

        // 2. Combined ("1d 2h 30m") or Simple ("3h", "1.5d") 형식
        let combinedOrSimpleMinutes = 0;
        let matched = false;
        const parts = durationString.toLowerCase().match(/(\d+(\.\d+)?\s*[dhms])/g) || [];
        for (const part of parts) {
            const value = parseFloat(part);
            if (isNaN(value)) continue;
            if (part.includes('d')) { combinedOrSimpleMinutes += value * MINUTES_PER_DAY; matched = true;}
            else if (part.includes('h')) { combinedOrSimpleMinutes += value * MINUTES_PER_HOUR; matched = true;}
            else if (part.includes('m')) { combinedOrSimpleMinutes += value; matched = true; }
        }
         if (matched) {
             // logDebug(`parseDurationToMinutes (Combined/Simple): '${durationString}' -> ${Math.round(combinedOrSimpleMinutes)}분`);
             return Math.round(combinedOrSimpleMinutes);
         }

        // 3. 숫자만 있는 경우 (분으로 간주)
        const numberOnlyMatch = durationString.match(/^(\d+(\.\d+)?)$/);
        if (numberOnlyMatch) {
            totalMinutes = parseFloat(numberOnlyMatch[1]);
             // logDebug(`parseDurationToMinutes (Number Only): '${durationString}' -> ${Math.round(totalMinutes)}분 (분으로 간주)`);
            return Math.round(totalMinutes);
        }

        logDebug(`parseDurationToMinutes: '${durationString}' 형식을 인식할 수 없음.`);
        return null;
    } catch (error) {
        // console.error 대신 dv.paragraph 사용
        dv.paragraph(`❌ **파싱 오류:** '${durationString}' 기간 파싱 중 오류 발생: ${error.message}`);
        logDebug("parseDurationToMinutes 오류 발생", error); // 콘솔에는 여전히 로그 남김 (디버깅용)
        return null;
    }
};

/**
 * 총 분(minute)을 "Xd Yh Zm" 형식의 문자열로 변환합니다.
 * @param {number|null} totalMinutes - 변환할 총 분. null이면 '-' 반환.
 * @returns {string} 포맷된 시간 문자열
 */
const formatMinutesToDHMS = (totalMinutes) => {
    if (totalMinutes === null || typeof totalMinutes !== 'number' || isNaN(totalMinutes)) {
        return "-";
    }
    if (totalMinutes === 0) return "0m";
    const sign = totalMinutes < 0 ? "-" : "";
    let absMinutes = Math.abs(Math.round(totalMinutes));
    const days = Math.floor(absMinutes / MINUTES_PER_DAY);
    absMinutes %= MINUTES_PER_DAY;
    const hours = Math.floor(absMinutes / MINUTES_PER_HOUR);
    absMinutes %= MINUTES_PER_HOUR;
    const minutes = absMinutes;
    let result = "";
    if (days > 0) result += `${days}d `;
    if (hours > 0) result += `${hours}h `;
    if (minutes > 0 || (days === 0 && hours === 0)) { result += `${minutes}m`; }
    result = result.trim();
    return result ? sign + result : "0m";
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


// --- SCRIPT START ---
dv.paragraph("🚀 **Dataview Task Aggregator (Updated Regex & All Features)**"); // Title updated
logDebug("스크립트 실행 시작", { startDateRange, endDateRange, taskFolderPaths, dailyNoteFolder });

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
                    const projectRaw = taskPage.project;
                    const epicRaw = taskPage.epic;
                    const impactRaw = taskPage.impact;

                    let impactNumber = null;
                    if (impactRaw !== undefined && impactRaw !== null) {
                        const parsedImpact = parseFloat(impactRaw);
                        if (!isNaN(parsedImpact)) {
                            impactNumber = parsedImpact;
                        } else {
                            logDebug(`'${taskName}' Task의 impact 값(${impactRaw})을 숫자로 파싱할 수 없음.`);
                        }
                    }

                    const finalEstimatedRaw = (estimatedTimeRaw !== undefined && estimatedTimeRaw !== null && String(estimatedTimeRaw).trim() !== "") ? String(estimatedTimeRaw) : "-";
                    const finalProject = (projectRaw !== undefined && projectRaw !== null && String(projectRaw).trim() !== "") ? String(projectRaw) : "-";
                    const finalEpic = (epicRaw !== undefined && epicRaw !== null && String(epicRaw).trim() !== "") ? String(epicRaw) : "-";

                    if (taskName) {
                        if (!taskData.hasOwnProperty(taskName)) {
                            taskData[taskName] = {
                                estimatedRaw: finalEstimatedRaw,
                                project: finalProject,
                                epic: finalEpic,
                                impact: impactNumber,
                                sourcePath: taskFilePath
                            };
                            totalTasksLoaded++;
                        }
                    }
                }
            } else {
                foldersNotFound.push(currentFolderPath);
            }
        } catch (e) {
            dv.paragraph(`❌ **폴더 오류:** '${currentFolderPath}' 폴더 처리 중 오류 발생: ${e.message}. (경로 및 접근 권한 확인)`);
            logDebug(`폴더 처리 오류 (${currentFolderPath})`, e);
            foldersFailed.push(currentFolderPath);
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
                try {
                    fileContent = await dv.io.load(page.file.path);
                } catch (e) {
                    dv.paragraph(`❌ **파일 읽기 오류:** ${page.file.link} 내용 읽기 실패: ${e.message}.`);
                    logDebug(`데일리 노트 파일 읽기 실패: ${page.file.path}`, e);
                    dailyNotesFailed++;
                    continue;
                }

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
                    // ⭐ 정규식 수정: 시작 부분 리스트 마커 선택적, 시간 사이 구분자 허용, 시간 뒤 공백 필수
                    const lineRegex = /^\s*(?:[-*•]\s+)?(\d{1,2}:\d{2})\s*[-–~]\s*(\d{1,2}:\d{2})\s+(.*?)(?:\s+#.*)?$/;
                    let timeErrors = 0;

                    for (const line of lines) {
                        const trimmedLine = line.trim();
                        if (!trimmedLine || trimmedLine.startsWith('#')) continue;

                        logDebug(`처리 시도 라인 (${page.file.name}):`, trimmedLine);

                        const match = trimmedLine.match(lineRegex);
                        if (match) {
                            logDebug(`   -> 정규식 매칭 성공!`);
                            // 시간 형식 표준화 (HH:MM) - 정규식에서 이미 2자리로 잡도록 변경
                            let startTimeStr = match[1].padStart(5, '0');
                            let endTimeStr = match[2].padStart(5, '0');
                            let activityDisplay = match[3].trim();
                            let potentialTaskName = activityDisplay;
                            let estimatedRawResult = "-";
                            let projectResult = "-";
                            let epicResult = "-";
                            let impactResult = null;

                            const linkMatch = activityDisplay.match(/^!?\[\[(.*?)\]\]$/);
                            if (linkMatch && linkMatch[1]) {
                                potentialTaskName = linkMatch[1].trim();
                                activityDisplay = linkMatch[0];
                                logDebug(`   -> 링크 활동명. Task 이름: '${potentialTaskName}'`);
                            } else {
                                potentialTaskName = potentialTaskName
                                    .replace(/^\s*[\p{Emoji_Presentation}\p{Emoji}]\s*/u, '')
                                    .replace(/^[ *_~]+|[ *_~]+$/g, '')
                                    .replace(/[*_~]{1,3}(.*?)[*_~]{1,3}/g, '$1')
                                    .trim();
                                activityDisplay = potentialTaskName;
                                logDebug(`   -> 일반 텍스트 활동명. Task 이름: '${potentialTaskName}'`);
                            }

                            let taskExists = false;
                            if (taskData.hasOwnProperty(potentialTaskName)) {
                                taskExists = true;
                                const taskInfo = taskData[potentialTaskName];
                                estimatedRawResult = taskInfo.estimatedRaw;
                                projectResult = taskInfo.project;
                                epicResult = taskInfo.epic;
                                impactResult = taskInfo.impact;
                                logDebug(`   -> Task 매칭됨: '${potentialTaskName}'`);
                            } else {
                                logDebug(`   -> Task 매칭 안됨: '${potentialTaskName}'`);
                            }

                            let durationMinutes = 0;
                             try {
                                const start = new Date(`${currentNoteDateStr}T${startTimeStr}:00`);
                                const end = new Date(`${currentNoteDateStr}T${endTimeStr}:00`);
                                if (isNaN(start.getTime()) || isNaN(end.getTime())) {
                                    logDebug(`   -> 시간 변환 오류`); timeErrors++; continue;
                                }
                                // 날짜 넘어가는 경우 처리 (예: 23:00-01:00)
                                if (start >= end) {
                                    logDebug(`   -> 종료 시간이 시작 시간보다 빠르거나 같음. 날짜 조정 시도.`);
                                     end.setDate(end.getDate() + 1);
                                     logDebug(`   -> 조정된 종료 시간: ${end.toISOString()}`);
                                     if (start >= end) { // 조정 후에도 여전히 문제 있으면 건너뛰기
                                        logDebug(`   -> 날짜 조정 후에도 시간 순서 오류. 건너뜀.`); timeErrors++; continue;
                                     }
                                }
                                durationMinutes = (end - start) / (1000 * 60);
                                logDebug(`   -> 계산된 시간: ${durationMinutes.toFixed(2)}분`);
                                if (durationMinutes <= 0) continue;
                            } catch (e) {
                                dv.paragraph(`❌ **시간 처리 오류:** ${page.file.link}의 '${trimmedLine}' 처리 중 오류: ${e.message}`);
                                logDebug(`시간 처리 예외 발생 (${page.file.name}): ${trimmedLine}`, e);
                                timeErrors++;
                                continue;
                            }

                            if (taskExists) {
                                if (!activityDisplay) activityDisplay = "(설명 없음)";
                                allActivities.push({
                                    activityDisplay,
                                    duration: Math.round(durationMinutes),
                                    estimatedRaw: estimatedRawResult,
                                    project: projectResult,
                                    epic: epicResult,
                                    impact: impactResult
                                });
                                logDebug(`   => 활동 추가됨 (Task 존재): '${activityDisplay}', duration: ${Math.round(durationMinutes)}`);
                            } else {
                                totalDurationSkippedTasks += durationMinutes;
                                logDebug(`   => 활동 건너뜀 (Task 없음): '${activityDisplay}', 시간: ${durationMinutes.toFixed(2)}분`);
                            }
                        } else {
                            logDebug("   -> 정규식 매칭 실패 (처리 안함)");
                        }
                    } // End of line loop
                     if (timeErrors > 0) dv.paragraph(`⚠️ ${page.file.link} 처리 중 ${timeErrors}개의 시간 관련 오류/경고 발생.`);
                } else if (sectionContent === "") {
                    // logDebug(`'Day planner' 섹션 내용 없음 (${page.file.name})`);
                }
            } else {
                 if (/^\d{4}-\d{2}-\d{2}$/.test(fileName)) { /* 날짜 범위 벗어남 */ }
            }
        } else { /* 파일명 형식 안맞음 */ }
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
        acc[activityDisplay].totalDuration += duration;
        return acc;
    }, {});
    logDebug("최종 활동별 집계 결과 (Task 존재하는 것만):", grouped);

    if (Object.keys(grouped).length > 0) {
        dv.paragraph(`--- 전체 기간 활동 요약 (${startDateRange} ~ ${endDateRange}) ---`);

        const dataForTable = Object.entries(grouped).map(([activity, data]) => {
            const estimatedMinutes = parseDurationToMinutes(data.estimatedRaw);
            const impact = data.impact;
            let priority = -Infinity;

            if (isNumber(impact) && isNumber(estimatedMinutes) && estimatedMinutes > 0) {
                priority = impact / estimatedMinutes;
            }

            return {
                activity,
                project: data.project,
                epic: data.epic,
                impact: isNumber(impact) ? impact : "-",
                totalDurationMinutes: data.totalDuration,
                estimatedMinutes: estimatedMinutes,
                priority: priority
            };
        });

        dataForTable.sort((a, b) => b.priority - a.priority);
        logDebug("Priority 기준 정렬 후 데이터:", dataForTable);

        const header = `| 활동 (Activity) | Project | Epic | Impact | Priority | 총 소요 시간 (Total) | 예상 시간 (Estimated) | 남은 시간 (Remaining) |
| :-------------- | :------ | :--- | :----- | :------- | :------------------- | :-------------------- | :-------------------- |`;

        const rows = dataForTable.map(item => {
            let remainingMinutes = null;
            if (isNumber(item.estimatedMinutes)) {
                remainingMinutes = item.estimatedMinutes - item.totalDurationMinutes;
            }
            const totalFormatted = formatMinutesToDHMS(item.totalDurationMinutes);
            const estimatedFormatted = formatMinutesToDHMS(item.estimatedMinutes);
            const remainingFormatted = formatMinutesToDHMS(remainingMinutes);
            const priorityFormatted = isFinite(item.priority) && item.priority > -Infinity ? item.priority.toFixed(2) : "-";

            const escapePipe = (str) => String(str).replace(/\|/g, "\\|");

            return `| ${escapePipe(item.activity)} | ${escapePipe(item.project)} | ${escapePipe(item.epic)} | ${escapePipe(item.impact)} | ${priorityFormatted} | ${totalFormatted} | ${estimatedFormatted} | ${remainingFormatted} |`;
        });


        dv.paragraph(header + "\n" + rows.join("\n"));
    } else {
         dv.paragraph("ℹ️ 유효한 활동 그룹이 없습니다 (Task와 매칭된 활동 없음).");
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
const startDateRange = "2025-04-30"; // <--- !!! 시작 날짜 수정 !!!
const endDateRange = "2025-04-30";   // <--- !!! 종료 날짜 수정 !!!

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
        dv.paragraph(`[Dataview Debug] ${message}`, data !== undefined ? data : "");
    }
};

/**
 * 다양한 형식의 기간 문자열을 총 분(minute) 단위로 파싱합니다.
 * @param {string} durationString - 파싱할 기간 문자열
 * @returns {number|null} 총 분(minute) 또는 파싱 실패 시 null
 */
const parseDurationToMinutes = (durationString) => {
    if (!durationString || typeof durationString !== 'string' || durationString.trim() === "" || durationString.trim() === "-") {
        return null;
    }
    durationString = durationString.trim();
    let totalMinutes = 0;
    try {
        // 1. ISO 8601 Duration 형식 (예: P1DT2H30M, PT10H)
        if (durationString.startsWith('P')) {
            let remainingString = durationString.substring(1);
            let timePart = remainingString.split('T')[1] || '';
            let datePart = remainingString.split('T')[0];
            const dayMatch = datePart.match(/(\d+(\.\d+)?)D/);
            if (dayMatch) totalMinutes += parseFloat(dayMatch[1]) * MINUTES_PER_DAY;
            const hourMatch = timePart.match(/(\d+(\.\d+)?)H/);
            if (hourMatch) totalMinutes += parseFloat(hourMatch[1]) * MINUTES_PER_HOUR;
            const minuteMatch = timePart.match(/(\d+(\.\d+)?)M/);
            if (minuteMatch) totalMinutes += parseFloat(minuteMatch[1]);
            if (totalMinutes > 0 || dayMatch || hourMatch || minuteMatch) {
                 logDebug(`parseDurationToMinutes (ISO): '${durationString}' -> ${Math.round(totalMinutes)}분`);
                 return Math.round(totalMinutes);
            }
            logDebug(`parseDurationToMinutes (ISO): '${durationString}' 에서 유효 시간 단위 못찾음. 다른 형식 시도.`);
            totalMinutes = 0;
        }

        // 2. Combined ("1d 2h 30m") or Simple ("3h", "1.5d") 형식
        let combinedOrSimpleMinutes = 0;
        let matched = false;
        // Combined: "1d 2h 30m" -> ["1d", "2h", "30m"]
        // Simple: "3h" -> ["3h"]
        const parts = durationString.toLowerCase().match(/(\d+(\.\d+)?\s*[dhms])/g) || []; // d, h, m, s 단위 매칭 (s는 무시됨)
        for (const part of parts) {
            const value = parseFloat(part);
            if (isNaN(value)) continue;

            if (part.includes('d')) { combinedOrSimpleMinutes += value * MINUTES_PER_DAY; matched = true;}
            else if (part.includes('h')) { combinedOrSimpleMinutes += value * MINUTES_PER_HOUR; matched = true;}
            else if (part.includes('m')) { combinedOrSimpleMinutes += value; matched = true; }
            // s (초)는 무시
        }
         if (matched) {
             logDebug(`parseDurationToMinutes (Combined/Simple): '${durationString}' -> ${Math.round(combinedOrSimpleMinutes)}분`);
             return Math.round(combinedOrSimpleMinutes);
         }

        // 3. 숫자만 있는 경우 (분으로 간주)
        const numberOnlyMatch = durationString.match(/^(\d+(\.\d+)?)$/);
        if (numberOnlyMatch) {
            totalMinutes = parseFloat(numberOnlyMatch[1]);
             logDebug(`parseDurationToMinutes (Number Only): '${durationString}' -> ${Math.round(totalMinutes)}분 (분으로 간주)`);
            return Math.round(totalMinutes);
        }

        logDebug(`parseDurationToMinutes: '${durationString}' 형식을 인식할 수 없음.`);
        return null;
    } catch (error) {
        console.error(`[Dataview Error] parseDurationToMinutes('${durationString}') 파싱 중 오류:`, error);
        return null;
    }
};

/**
 * 총 분(minute)을 "Xd Yh Zm" 형식의 문자열로 변환합니다.
 * @param {number|null} totalMinutes - 변환할 총 분. null이면 '-' 반환.
 * @returns {string} 포맷된 시간 문자열
 */
const formatMinutesToDHMS = (totalMinutes) => {
    if (totalMinutes === null || typeof totalMinutes !== 'number' || isNaN(totalMinutes)) {
        return "-";
    }
    if (totalMinutes === 0) return "0m";
    const sign = totalMinutes < 0 ? "-" : "";
    let absMinutes = Math.abs(Math.round(totalMinutes));
    const days = Math.floor(absMinutes / MINUTES_PER_DAY);
    absMinutes %= MINUTES_PER_DAY;
    const hours = Math.floor(absMinutes / MINUTES_PER_HOUR);
    absMinutes %= MINUTES_PER_HOUR;
    const minutes = absMinutes;
    let result = "";
    if (days > 0) result += `${days}d `;
    if (hours > 0) result += `${hours}h `;
    if (minutes > 0 || (days === 0 && hours === 0)) { result += `${minutes}m`; }
    result = result.trim();
    return result ? sign + result : "0m";
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


// --- SCRIPT START ---
dv.paragraph("🚀 **Dataview Task Aggregator (Refined Parsing & All Features)**"); // Title updated
logDebug("스크립트 실행 시작", { startDateRange, endDateRange, taskFolderPaths, dailyNoteFolder });

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
                    const projectRaw = taskPage.project;
                    const epicRaw = taskPage.epic;
                    const impactRaw = taskPage.impact;

                    let impactNumber = null;
                    if (impactRaw !== undefined && impactRaw !== null) {
                        const parsedImpact = parseFloat(impactRaw);
                        if (!isNaN(parsedImpact)) {
                            impactNumber = parsedImpact;
                        } else {
                            logDebug(`'${taskName}' Task의 impact 값(${impactRaw})을 숫자로 파싱할 수 없음.`);
                        }
                    }

                    const finalEstimatedRaw = (estimatedTimeRaw !== undefined && estimatedTimeRaw !== null && String(estimatedTimeRaw).trim() !== "") ? String(estimatedTimeRaw) : "-";
                    const finalProject = (projectRaw !== undefined && projectRaw !== null && String(projectRaw).trim() !== "") ? String(projectRaw) : "-";
                    const finalEpic = (epicRaw !== undefined && epicRaw !== null && String(epicRaw).trim() !== "") ? String(epicRaw) : "-";

                    if (taskName) {
                        if (!taskData.hasOwnProperty(taskName)) {
                            taskData[taskName] = {
                                estimatedRaw: finalEstimatedRaw,
                                project: finalProject,
                                epic: finalEpic,
                                impact: impactNumber,
                                sourcePath: taskFilePath
                            };
                            totalTasksLoaded++;
                        }
                    }
                }
            } else {
                foldersNotFound.push(currentFolderPath);
            }
        } catch (e) {
            console.error(`[Dataview Error] '${currentFolderPath}' 폴더 처리 중 오류:`, e);
            dv.paragraph(`❌ **폴더 오류:** '${currentFolderPath}' 폴더 처리 중 오류 발생. (개발자 콘솔 확인)`);
            foldersFailed.push(currentFolderPath);
        }
    }
    dv.paragraph(`✅ Task 로딩 완료: ${foldersSearched}개 폴더 검색 시도. ${foldersFound.length}개 폴더에서 ${totalTasksLoaded}개 고유 Task 로드.`);
    if (foldersNotFound.length > 0) dv.paragraph(`ℹ️ 파일 없음: ${foldersNotFound.join(', ')} 폴더에서는 Task 파일을 찾지 못했습니다.`);
    if (foldersFailed.length > 0) dv.paragraph(`❌ 로딩 실패: ${foldersFailed.join(', ')} 폴더 처리 중 오류 발생.`);
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
                try {
                    fileContent = await dv.io.load(page.file.path);
                } catch (e) {
                    console.error(`[Dataview Error] 데일리 노트 파일 읽기 실패: ${page.file.path}`, e);
                    dv.paragraph(`❌ **파일 읽기 오류:** ${page.file.link} 내용 읽기 실패.`);
                    dailyNotesFailed++;
                    continue;
                }

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
                    // 정규식 수정: 시작 부분 `-` 또는 `*` 또는 `•` 허용, 시간 사이 구분자 `-`, `–`, `~` 허용
                    const lineRegex = /^\s*[-*•]\s+(\d{2}:\d{2})\s*[-–~]\s*(\d{2}:\d{2})\s+(.*?)(?:\s+#.*)?$/;
                    let timeErrors = 0;

                    for (const line of lines) {
                        const trimmedLine = line.trim();
                        // 빈 줄 건너뛰기 추가
                        if (!trimmedLine || trimmedLine.startsWith('#')) continue;

                        logDebug(`처리 시도 라인 (${page.file.name}):`, trimmedLine); // ⚠️ 모든 줄 로깅

                        const match = trimmedLine.match(lineRegex);
                        if (match) {
                            logDebug(`   -> 정규식 매칭 성공!`); // ⚠️ 매칭 성공 로그
                            const startTimeStr = match[1];
                            const endTimeStr = match[2];
                            let activityDisplay = match[3].trim();
                            let potentialTaskName = activityDisplay;
                            let estimatedRawResult = "-";
                            let projectResult = "-";
                            let epicResult = "-";
                            let impactResult = null;

                            const linkMatch = activityDisplay.match(/^!?\[\[(.*?)\]\]$/);
                            if (linkMatch && linkMatch[1]) {
                                potentialTaskName = linkMatch[1].trim();
                                activityDisplay = linkMatch[0];
                                logDebug(`   -> 링크 활동명. Task 이름: '${potentialTaskName}'`);
                            } else {
                                potentialTaskName = potentialTaskName
                                    .replace(/^\s*[\p{Emoji_Presentation}\p{Emoji}]\s*/u, '')
                                    .replace(/^[ *_~]+|[ *_~]+$/g, '')
                                    .replace(/[*_~]{1,3}(.*?)[*_~]{1,3}/g, '$1')
                                    .trim();
                                activityDisplay = potentialTaskName;
                                logDebug(`   -> 일반 텍스트 활동명. Task 이름: '${potentialTaskName}'`);
                            }

                            let taskExists = false;
                            if (taskData.hasOwnProperty(potentialTaskName)) {
                                taskExists = true;
                                const taskInfo = taskData[potentialTaskName];
                                estimatedRawResult = taskInfo.estimatedRaw;
                                projectResult = taskInfo.project;
                                epicResult = taskInfo.epic;
                                impactResult = taskInfo.impact;
                                logDebug(`   -> Task 매칭됨: '${potentialTaskName}'`);
                            } else {
                                logDebug(`   -> Task 매칭 안됨: '${potentialTaskName}'`);
                            }

                            let durationMinutes = 0;
                             try {
                                const start = new Date(`${currentNoteDateStr}T${startTimeStr}:00`);
                                const end = new Date(`${currentNoteDateStr}T${endTimeStr}:00`);
                                if (isNaN(start.getTime()) || isNaN(end.getTime())) {
                                    logDebug(`   -> 시간 변환 오류`); timeErrors++; continue;
                                }
                                if (start >= end) {
                                     logDebug(`   -> 시간 순서 오류`); timeErrors++; continue;
                                }
                                durationMinutes = (end - start) / (1000 * 60);
                                logDebug(`   -> 계산된 시간: ${durationMinutes.toFixed(2)}분`);

                                if (durationMinutes <= 0) continue;

                            } catch (e) {
                                console.error(`[Dataview Error] 시간 처리 중 예외 발생 (${page.file.name}): ${trimmedLine}`, e);
                                dv.paragraph(`❌ 시간 처리 예외 발생 (${page.file.link}): ${trimmedLine}`);
                                timeErrors++;
                                continue;
                            }

                            if (taskExists) { // Task가 존재할 때만 allActivities에 추가
                                if (!activityDisplay) activityDisplay = "(설명 없음)";
                                allActivities.push({
                                    activityDisplay,
                                    duration: Math.round(durationMinutes),
                                    estimatedRaw: estimatedRawResult,
                                    project: projectResult,
                                    epic: epicResult,
                                    impact: impactResult
                                });
                                logDebug(`   => 활동 추가됨 (Task 존재): '${activityDisplay}', duration: ${Math.round(durationMinutes)}`);
                            } else { // Task가 없을 경우 건너뛴 시간 기록
                                totalDurationSkippedTasks += durationMinutes;
                                logDebug(`   => 활동 건너뜀 (Task 없음): '${activityDisplay}', 시간: ${durationMinutes.toFixed(2)}분`);
                            }
                        } else {
                            logDebug("   -> 정규식 매칭 실패 (처리 안함)"); // ⚠️ 매칭 실패 로그
                        }
                    } // End of line loop
                     if (timeErrors > 0) dv.paragraph(`⚠️ ${page.file.link} 처리 중 ${timeErrors}개의 시간 관련 오류/경고 발생.`);
                } else if (sectionContent === "") {
                    // logDebug(`'Day planner' 섹션 내용 없음 (${page.file.name})`);
                }
            } else {
                 if (/^\d{4}-\d{2}-\d{2}$/.test(fileName)) { /* 날짜 범위 벗어남 */ }
            }
        } else { /* 파일명 형식 안맞음 */ }
    } // End of page loop

    dv.paragraph(`✅ 데일리 노트 처리 완료: 총 ${dailyNotesProcessed}개 파일 분석 완료. ${dailyNotesFailed}개 파일 읽기 실패.`);
    if (totalDurationSkippedTasks > 0) {
         dv.paragraph(`ℹ️ **참고:** Task 파일이 없어 집계에서 제외된 활동들의 총 시간은 약 ${formatMinutesToDHMS(totalDurationSkippedTasks)} 입니다.`);
    }

} catch (e) {
    console.error(`[Dataview Error] 데일리 노트 폴더('${dailyNoteFolder}') 처리 중 오류:`, e);
    dv.paragraph(`❌ **폴더 처리 오류:** 데일리 노트 폴더 처리 중 오류 발생. (개발자 콘솔 확인)`);
}


// 3️⃣ 최종 결과 집계 및 출력 (Aggregate Final Results and Render)
if (allActivities.length > 0) {
    logDebug("최종 결과 집계 시작. Task와 매칭된 활동 항목 수:", allActivities.length);

    const grouped = allActivities.reduce((acc, { activityDisplay, duration, estimatedRaw, project, epic, impact }) => {
        if (!acc[activityDisplay]) {
            acc[activityDisplay] = { totalDuration: 0, estimatedRaw: estimatedRaw, project: project, epic: epic, impact: impact };
        }
        acc[activityDisplay].totalDuration += duration;
        return acc;
    }, {});
    logDebug("최종 활동별 집계 결과 (Task 존재하는 것만):", grouped);

    if (Object.keys(grouped).length > 0) {
        dv.paragraph(`--- 전체 기간 활동 요약 (${startDateRange} ~ ${endDateRange}) ---`);

        const dataForTable = Object.entries(grouped).map(([activity, data]) => {
            const estimatedMinutes = parseDurationToMinutes(data.estimatedRaw);
            const impact = data.impact;
            let priority = -Infinity;

            if (isNumber(impact) && isNumber(estimatedMinutes) && estimatedMinutes > 0) {
                priority = impact / estimatedMinutes;
            }

            return {
                activity,
                project: data.project,
                epic: data.epic,
                impact: isNumber(impact) ? impact : "-",
                totalDurationMinutes: data.totalDuration,
                estimatedMinutes: estimatedMinutes,
                priority: priority
            };
        });

        dataForTable.sort((a, b) => b.priority - a.priority);
        logDebug("Priority 기준 정렬 후 데이터:", dataForTable);

        const header = `| 활동 (Activity) | Project | Epic | Impact | Priority | 총 소요 시간 (Total) | 예상 시간 (Estimated) | 남은 시간 (Remaining) |
| :-------------- | :------ | :--- | :----- | :------- | :------------------- | :-------------------- | :-------------------- |`;

        const rows = dataForTable.map(item => {
            let remainingMinutes = null;
            if (isNumber(item.estimatedMinutes)) {
                remainingMinutes = item.estimatedMinutes - item.totalDurationMinutes;
            }
            const totalFormatted = formatMinutesToDHMS(item.totalDurationMinutes);
            const estimatedFormatted = formatMinutesToDHMS(item.estimatedMinutes);
            const remainingFormatted = formatMinutesToDHMS(remainingMinutes);
            const priorityFormatted = isFinite(item.priority) && item.priority > -Infinity ? item.priority.toFixed(2) : "-";

            return `| ${item.activity.replace(/\|/g, "\\|")} | ${item.project.replace(/\|/g, "\\|")} | ${item.epic.replace(/\|/g, "\\|")} | ${String(item.impact).replace(/\|/g, "\\|")} | ${priorityFormatted} | ${totalFormatted} | ${estimatedFormatted} | ${remainingFormatted} |`;
        });

        dv.paragraph(header + "\n" + rows.join("\n"));
    } else {
         dv.paragraph("ℹ️ 유효한 활동 그룹이 없습니다 (Task와 매칭된 활동 없음).");
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
const startDateRange = "2025-04-20"; // <--- !!! 시작 날짜 수정 !!!
const endDateRange = "2025-05-02";   // <--- !!! 종료 날짜 수정 !!!

// 📂 Task 파일들이 있는 폴더 경로 리스트 (List of Task Folder Paths)
const taskFolderPaths = [
    "02_Projects/Career/Grizzly Ridge/Task", // <--- 사용자 요청 경로 1
    "02_Projects/Career/Ratel2/Task",       // <--- 사용자 요청 경로 2
    "02_Projects/Career/Life Management Tool/Task",       // <--- 사용자 요청 경로 2
    // "Tasks",
    // "02 - Areas/Action",
    // "Projects/My Project/Tasks"
];

// 📓 데일리 노트가 있는 폴더 경로 (Daily Notes Folder Path)
const dailyNoteFolder = "01_Daily/Daily"; // <--- !!! 자신의 데일리 노트 폴더 경로로 수정하세요 !!!

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
 * @param {string} durationString - 파싱할 기간 문자열
 * @returns {number|null} 총 분(minute) 또는 파싱 실패 시 null
 */
const parseDurationToMinutes = (durationString) => {
    if (!durationString || typeof durationString !== 'string' || durationString.trim() === "" || durationString.trim() === "-") {
        return null;
    }
    durationString = durationString.trim();
    let totalMinutes = 0;
    try {
        if (durationString.startsWith('P')) { // ISO 8601 Duration
            let remainingString = durationString.substring(1);
            let timePart = remainingString.split('T')[1] || '';
            let datePart = remainingString.split('T')[0];
            const dayMatch = datePart.match(/(\d+(\.\d+)?)D/);
            if (dayMatch) totalMinutes += parseFloat(dayMatch[1]) * MINUTES_PER_DAY;
            const hourMatch = timePart.match(/(\d+(\.\d+)?)H/);
            if (hourMatch) totalMinutes += parseFloat(hourMatch[1]) * MINUTES_PER_HOUR;
            const minuteMatch = timePart.match(/(\d+(\.\d+)?)M/);
            if (minuteMatch) totalMinutes += parseFloat(minuteMatch[1]);
            if (totalMinutes > 0 || dayMatch || hourMatch || minuteMatch) {
                 logDebug(`parseDurationToMinutes (ISO): '${durationString}' -> ${Math.round(totalMinutes)}분`);
                 return Math.round(totalMinutes);
            }
            logDebug(`parseDurationToMinutes (ISO): '${durationString}' 에서 유효 시간 단위 못찾음. 다른 형식 시도.`);
            totalMinutes = 0;
        }

        let combinedOrSimpleMinutes = 0;
        let matched = false;
        const parts = durationString.toLowerCase().split(/\s+/);
        for (const part of parts) { // Combined ("1d 2h 30m") or Simple ("3h", "1.5d")
            const dayMatch = part.match(/^(\d+(\.\d+)?)d$/);
            if (dayMatch) { combinedOrSimpleMinutes += parseFloat(dayMatch[1]) * MINUTES_PER_DAY; matched = true; continue; }
            const hourMatch = part.match(/^(\d+(\.\d+)?)h$/);
            if (hourMatch) { combinedOrSimpleMinutes += parseFloat(hourMatch[1]) * MINUTES_PER_HOUR; matched = true; continue; }
            const minuteMatch = part.match(/^(\d+(\.\d+)?)m$/);
            if (minuteMatch) { combinedOrSimpleMinutes += parseFloat(minuteMatch[1]); matched = true; continue; }
        }
        if (matched) {
             logDebug(`parseDurationToMinutes (Combined/Simple): '${durationString}' -> ${Math.round(combinedOrSimpleMinutes)}분`);
             return Math.round(combinedOrSimpleMinutes);
        }

        const numberOnlyMatch = durationString.match(/^(\d+(\.\d+)?)$/); // 숫자만 (분으로 간주, 소수점 허용)
        if (numberOnlyMatch) {
            totalMinutes = parseFloat(numberOnlyMatch[1]);
             logDebug(`parseDurationToMinutes (Number Only): '${durationString}' -> ${Math.round(totalMinutes)}분 (분으로 간주)`);
            return Math.round(totalMinutes);
        }

        logDebug(`parseDurationToMinutes: '${durationString}' 형식을 인식할 수 없음.`);
        return null;
    } catch (error) {
        console.error(`[Dataview Error] parseDurationToMinutes('${durationString}') 파싱 중 오류:`, error);
        return null;
    }
};

/**
 * 총 분(minute)을 "Xd Yh Zm" 형식의 문자열로 변환합니다.
 * @param {number|null} totalMinutes - 변환할 총 분. null이면 '-' 반환.
 * @returns {string} 포맷된 시간 문자열
 */
const formatMinutesToDHMS = (totalMinutes) => {
    if (totalMinutes === null || typeof totalMinutes !== 'number' || isNaN(totalMinutes)) {
        return "-";
    }
    if (totalMinutes === 0) return "0m";
    const sign = totalMinutes < 0 ? "-" : "";
    let absMinutes = Math.abs(Math.round(totalMinutes));
    const days = Math.floor(absMinutes / MINUTES_PER_DAY);
    absMinutes %= MINUTES_PER_DAY;
    const hours = Math.floor(absMinutes / MINUTES_PER_HOUR);
    absMinutes %= MINUTES_PER_HOUR;
    const minutes = absMinutes;
    let result = "";
    if (days > 0) result += `${days}d `;
    if (hours > 0) result += `${hours}h `;
    if (minutes > 0 || (days === 0 && hours === 0)) { result += `${minutes}m`; }
    result = result.trim();
    return result ? sign + result : "0m";
};

/**
 * YAML frontmatter 날짜 형식이 유효한지 확인합니다.
 */
const isValidDateString = (dateString) => {
    return /^\d{4}-\d{2}-\d{2}$/.test(dateString) && !isNaN(new Date(dateString));
};

/**
 * 숫자인지 확인하는 간단한 함수
 * @param {any} value
 * @returns {boolean}
 */
const isNumber = (value) => typeof value === 'number' && !isNaN(value);


// --- SCRIPT START ---
dv.paragraph("🚀 **Dataview Task Aggregator (Priority Column & Sort)**"); // Title updated
logDebug("스크립트 실행 시작", { startDateRange, endDateRange, taskFolderPaths, dailyNoteFolder });

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
// Task 이름(키)과 { estimatedRaw: string, project: string, epic: string, impact: number|null, sourcePath: string } (값)을 저장
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
                logDebug(`'${currentFolderPath}' 폴더에서 ${taskPages.length}개의 파일을 찾았습니다.`);
                for (const taskPage of taskPages) {
                    const taskName = taskPage.file.name;
                    const taskFilePath = taskPage.file.path;
                    const estimatedTimeRaw = taskPage.estimated;
                    const projectRaw = taskPage.project;
                    const epicRaw = taskPage.epic;
                    const impactRaw = taskPage.impact; // impact 값 읽기

                    logDebug(`처리 중인 Task 파일: '${taskFilePath}', 이름: '${taskName}'`);
                    logDebug(`   -> Frontmatter 'estimated' 원시 값:`, estimatedTimeRaw);
                    logDebug(`   -> Frontmatter 'project' 원시 값:`, projectRaw);
                    logDebug(`   -> Frontmatter 'epic' 원시 값:`, epicRaw);
                    logDebug(`   -> Frontmatter 'impact' 원시 값:`, impactRaw);

                    // impact 값을 숫자로 파싱, 실패 시 null
                    let impactNumber = null;
                    if (impactRaw !== undefined && impactRaw !== null) {
                        const parsedImpact = parseFloat(impactRaw);
                        if (!isNaN(parsedImpact)) {
                            impactNumber = parsedImpact;
                            logDebug(`   -> 파싱된 'impactNumber': ${impactNumber}`);
                        } else {
                            logDebug(`   -> 'impact' 값(${impactRaw})을 숫자로 파싱할 수 없음.`);
                        }
                    } else {
                         logDebug(`   -> 'impact' 값이 없거나 null임.`);
                    }

                    // 값이 없거나 비어있으면 '-'로 처리 (문자열 필드)
                    const finalEstimatedRaw = (estimatedTimeRaw !== undefined && estimatedTimeRaw !== null && String(estimatedTimeRaw).trim() !== "") ? String(estimatedTimeRaw) : "-";
                    const finalProject = (projectRaw !== undefined && projectRaw !== null && String(projectRaw).trim() !== "") ? String(projectRaw) : "-";
                    const finalEpic = (epicRaw !== undefined && epicRaw !== null && String(epicRaw).trim() !== "") ? String(epicRaw) : "-";
                    // impact는 파싱된 숫자 또는 null 저장

                    if (taskName) {
                        if (!taskData.hasOwnProperty(taskName)) {
                            taskData[taskName] = {
                                estimatedRaw: finalEstimatedRaw,
                                project: finalProject,
                                epic: finalEpic,
                                impact: impactNumber, // 파싱된 impact 숫자 저장
                                sourcePath: taskFilePath
                            };
                            logDebug(`   => Task 데이터 저장: '${taskName}' = { estimatedRaw: '${finalEstimatedRaw}', project: '${finalProject}', epic: '${finalEpic}', impact: ${impactNumber}, sourcePath: '${taskFilePath}' }`);
                            totalTasksLoaded++;
                        } else {
                            logDebug(`   => 중복 Task 건너뜀: '${taskName}' (이미 '${taskData[taskName].sourcePath}' 에서 로드됨)`);
                        }
                    } else {
                        logDebug("   => 파일 이름이 없는 Task 페이지 건너뜀:", taskFilePath);
                    }
                }
            } else {
                foldersNotFound.push(currentFolderPath);
                logDebug(`'${currentFolderPath}' 폴더에 파일이 없습니다.`);
            }
        } catch (e) {
            console.error(`[Dataview Error] '${currentFolderPath}' 폴더 처리 중 오류:`, e);
            dv.paragraph(`❌ **폴더 오류:** '${currentFolderPath}' 폴더 처리 중 오류 발생. (개발자 콘솔 확인)`);
            foldersFailed.push(currentFolderPath);
        }
    }
    // Task 로딩 결과 요약
    dv.paragraph(`✅ Task 로딩 완료: ${foldersSearched}개 폴더 검색 시도. ${foldersFound.length}개 폴더에서 ${totalTasksLoaded}개 고유 Task 로드.`);
    if (foldersNotFound.length > 0) dv.paragraph(`ℹ️ 파일 없음: ${foldersNotFound.join(', ')} 폴더에서는 Task 파일을 찾지 못했습니다.`);
    if (foldersFailed.length > 0) dv.paragraph(`❌ 로딩 실패: ${foldersFailed.join(', ')} 폴더 처리 중 오류 발생.`);
    if (totalTasksLoaded === 0 && foldersSearched > 0 && foldersFailed.length === 0) dv.paragraph(`⚠️ **Task 없음:** 지정된 폴더들에서 유효한 Task 파일을 찾을 수 없습니다.`);
    if (taskFolderPaths.length > 1) dv.paragraph("ℹ️ *참고: 동일 이름 Task는 리스트에서 먼저 검색된 폴더의 정보 사용.*");
    logDebug("최종 로드된 Task 데이터 (impact 숫자 포함):", taskData);
}

// 2️⃣ 지정된 기간 내 데일리 노트 처리 (Process Daily Notes within Date Range)
dv.paragraph(`📄 데일리 노트 분석 시작: ${dailyNoteFolder} 폴더 (${startDateRange} ~ ${endDateRange})`);
logDebug("분석할 데일리 노트 폴더:", dailyNoteFolder);

const allActivities = []; // 모든 데일리 노트의 유효한 활동을 저장할 배열
let dailyNotesProcessed = 0;
let dailyNotesFailed = 0;

try {
    const dailyPages = dv.pages(`"${dailyNoteFolder}"`);
    logDebug(`${dailyNoteFolder} 폴더에서 ${dailyPages.length}개의 파일을 찾았습니다.`);

    for (const page of dailyPages) {
        const fileName = page.file.name;
        if (/^\d{4}-\d{2}-\d{2}$/.test(fileName)) {
            const currentNoteDateStr = fileName;
            const currentNoteDt = new Date(currentNoteDateStr);

            if (!isNaN(currentNoteDt) && currentNoteDt >= startDt && currentNoteDt <= endDt) {
                logDebug(`처리 대상 데일리 노트: ${page.file.link} (${currentNoteDateStr})`);
                dailyNotesProcessed++;

                let fileContent = null;
                try {
                    fileContent = await dv.io.load(page.file.path);
                } catch (e) {
                    console.error(`[Dataview Error] 데일리 노트 파일 읽기 실패: ${page.file.path}`, e);
                    dv.paragraph(`❌ **파일 읽기 오류:** ${page.file.link} 내용 읽기 실패.`);
                    dailyNotesFailed++;
                    continue;
                }

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
                    const lineRegex = /^\s*[-*•]\s+(?:\*\*?)?(\d{2}:\d{2})\s*[-–~]\s*(\d{2}:\d{2})(?:\*\*?)?\s*(.*?)(?:\s+#.*)?$/;
                    let timeErrors = 0;

                    for (const line of lines) {
                        const trimmedLine = line.trim();
                        if (!trimmedLine || trimmedLine.startsWith('#')) continue;

                        const match = trimmedLine.match(lineRegex);
                        if (match) {
                            const startTimeStr = match[1];
                            const endTimeStr = match[2];
                            let activityDisplay = match[3].trim();
                            let potentialTaskName = activityDisplay;
                            let estimatedRawResult = "-";
                            let projectResult = "-";
                            let epicResult = "-";
                            let impactResult = null; // impact 숫자 저장 (기본 null)

                            logDebug(`처리 중인 활동 라인 (${page.file.name}):`, trimmedLine);

                            // 활동 이름 정리 및 potentialTaskName 결정
                            const linkMatch = activityDisplay.match(/^!?\[\[(.*?)\]\]$/);
                            if (linkMatch && linkMatch[1]) {
                                potentialTaskName = linkMatch[1].trim();
                                activityDisplay = linkMatch[0];
                                logDebug(`   -> 링크 활동명 발견. 매칭 시도 Task 이름: '${potentialTaskName}'`);
                            } else {
                                potentialTaskName = potentialTaskName
                                    .replace(/^\s*[\p{Emoji_Presentation}\p{Emoji}]\s*/u, '')
                                    .replace(/^[ *_~]+|[ *_~]+$/g, '')
                                    .replace(/[*_~]{1,3}(.*?)[*_~]{1,3}/g, '$1')
                                    .trim();
                                activityDisplay = potentialTaskName;
                                logDebug(`   -> 일반 텍스트 활동명. 매칭 시도 Task 이름: '${potentialTaskName}'`);
                            }

                            // Task 존재 여부 확인 및 정보 가져오기 (impact 숫자 포함)
                            let taskExists = false;
                            if (taskData.hasOwnProperty(potentialTaskName)) {
                                taskExists = true;
                                const taskInfo = taskData[potentialTaskName];
                                estimatedRawResult = taskInfo.estimatedRaw;
                                projectResult = taskInfo.project;
                                epicResult = taskInfo.epic;
                                impactResult = taskInfo.impact; // 저장된 impact 숫자 또는 null
                                logDebug(`   -> Task 매칭 성공! '${potentialTaskName}' -> 가져온 정보: { estimatedRaw: '${estimatedRawResult}', project: '${projectResult}', epic: '${epicResult}', impact: ${impactResult} } (출처: ${taskInfo.sourcePath})`);
                            } else {
                                logDebug(`   -> Task 매칭 실패: '${potentialTaskName}'에 해당하는 Task를 taskData에서 찾을 수 없음.`);
                            }

                            // Task가 존재할 경우에만 시간 계산 및 활동 추가
                            if (taskExists) {
                                if (!activityDisplay) activityDisplay = "(설명 없음)";

                                try {
                                    const start = new Date(`${currentNoteDateStr}T${startTimeStr}:00`);
                                    const end = new Date(`${currentNoteDateStr}T${endTimeStr}:00`);

                                    if (isNaN(start.getTime()) || isNaN(end.getTime())) {
                                        logDebug(`   -> 시간 변환 오류 (Invalid Date) (${page.file.name})`); timeErrors++; continue;
                                    }
                                    if (start >= end) {
                                         logDebug(`   -> 시간 순서 오류 (Start >= End) (${page.file.name})`); timeErrors++; continue;
                                    }

                                    const duration = (end - start) / (1000 * 60); // 실제 소요 시간 (분)
                                    if (duration > 0) {
                                        // 유효한 활동 정보(Task 존재 확인됨)를 allActivities 배열에 추가 (impact 숫자 포함)
                                        allActivities.push({
                                            activityDisplay,
                                            duration: Math.round(duration),
                                            estimatedRaw: estimatedRawResult,
                                            project: projectResult,
                                            epic: epicResult,
                                            impact: impactResult // impact 숫자 또는 null 추가
                                        });
                                        logDebug(`   => 유효 활동 추가됨: { activity: '${activityDisplay}', duration: ${Math.round(duration)}, estimatedRaw: '${estimatedRawResult}', project: '${projectResult}', epic: '${epicResult}', impact: ${impactResult} }`);
                                    } else {
                                         logDebug(`   -> 계산된 시간이 0 이하 (${page.file.name}):`, { duration });
                                    }
                                } catch (e) {
                                    console.error(`[Dataview Error] 시간 처리 중 예외 발생 (${page.file.name}): ${trimmedLine}`, e);
                                    dv.paragraph(`❌ 시간 처리 예외 발생 (${page.file.link}): ${trimmedLine} (개발자 콘솔 확인)`);
                                    timeErrors++;
                                }
                            } // End if(taskExists)
                        } else {
                            logDebug("정규식 매칭 실패 (처리 안함):", trimmedLine);
                        }
                    } // End of line loop
                     if (timeErrors > 0) dv.paragraph(`⚠️ ${page.file.link} 처리 중 ${timeErrors}개의 시간 관련 오류/경고 발생.`);
                } else if (sectionContent === "") {
                    logDebug(`'Day planner' 섹션 내용 없음 (${page.file.name})`);
                }
            } else {
                 if (/^\d{4}-\d{2}-\d{2}$/.test(fileName)) logDebug(`날짜 범위 벗어남 또는 유효하지 않음: ${page.file.link}`);
            }
        } else { logDebug(`파일명 형식 안맞음 건너뜀: ${page.file.link}`); }
    } // End of page loop

    dv.paragraph(`✅ 데일리 노트 처리 완료: 총 ${dailyNotesProcessed}개 파일 분석 완료. ${dailyNotesFailed}개 파일 읽기 실패.`);

} catch (e) {
    console.error(`[Dataview Error] 데일리 노트 폴더('${dailyNoteFolder}') 처리 중 오류:`, e);
    dv.paragraph(`❌ **폴더 처리 오류:** 데일리 노트 폴더 처리 중 오류 발생. (개발자 콘솔 확인)`);
}


// 3️⃣ 최종 결과 집계 및 출력 (Aggregate Final Results and Render)
// allActivities 배열에는 이미 Task가 존재하는 활동들만 포함되어 있음
if (allActivities.length > 0) {
    logDebug("최종 결과 집계 시작. Task와 매칭된 활동 항목 수:", allActivities.length);

    const grouped = allActivities.reduce((acc, { activityDisplay, duration, estimatedRaw, project, epic, impact }) => { // impact 추가
        if (!acc[activityDisplay]) {
            logDebug(`새 활동 그룹 생성: '${activityDisplay}', 초기 값 할당: { estimatedRaw: '${estimatedRaw}', project: '${project}', epic: '${epic}', impact: ${impact} }`);
            // 그룹 초기화 시 impact 숫자 정보도 함께 저장
            acc[activityDisplay] = { totalDuration: 0, estimatedRaw: estimatedRaw, project: project, epic: epic, impact: impact };
        } else {
             logDebug(`기존 활동 그룹에 시간 추가: '${activityDisplay}', 추가 시간: ${duration}`);
             // estimatedRaw, project, epic, impact는 첫 번째 값 유지
        }
        acc[activityDisplay].totalDuration += duration; // 실제 소요 시간 누적
        return acc;
    }, {});
    logDebug("최종 활동별 집계 결과 (Task 존재하는 것만, impact 숫자 포함):", grouped);

    if (Object.keys(grouped).length > 0) {
        dv.paragraph(`--- 전체 기간 활동 요약 (${startDateRange} ~ ${endDateRange}) ---`);

        // --- Priority 계산 및 정렬 ---
        const dataForTable = Object.entries(grouped).map(([activity, data]) => {
            const estimatedMinutes = parseDurationToMinutes(data.estimatedRaw);
            const impact = data.impact; // 저장된 impact 숫자 또는 null
            let priority = -Infinity; // 기본 우선순위 (계산 불가 시)

            // Priority 계산: impact가 유효한 숫자이고, estimatedMinutes가 0보다 큰 유효한 숫자일 때만 계산
            if (isNumber(impact) && isNumber(estimatedMinutes) && estimatedMinutes > 0) {
                priority = impact / estimatedMinutes;
                logDebug(`Priority 계산: '${activity}' -> impact=${impact}, estimatedMinutes=${estimatedMinutes}, priority=${priority}`);
            } else {
                logDebug(`Priority 계산 불가: '${activity}' -> impact=${impact}, estimatedMinutes=${estimatedMinutes}. 기본값(-Infinity) 사용.`);
            }

            return { // 테이블 생성을 위한 데이터 객체 반환
                activity,
                project: data.project,
                epic: data.epic,
                impact: isNumber(impact) ? impact : "-", // Impact는 숫자 또는 '-' 표시
                totalDurationMinutes: data.totalDuration,
                estimatedMinutes: estimatedMinutes,
                priority: priority // 계산된 우선순위 저장
            };
        });

        // Priority 기준으로 내림차순 정렬 (높은 우선순위 먼저)
        dataForTable.sort((a, b) => b.priority - a.priority);
        logDebug("Priority 기준 정렬 후 데이터:", dataForTable);

        // --- 테이블 생성 ---
        // 테이블 헤더에 "Priority" 추가 (Impact 뒤, Total Time 앞)
        const header = `| 활동 (Activity) | Project | Epic | Impact | Priority | 총 소요 시간 (Total) | 예상 시간 (Estimated) | 남은 시간 (Remaining) |
| :-------------- | :------ | :--- | :----- | :------- | :------------------- | :-------------------- | :-------------------- |`;

        const rows = dataForTable.map(item => {
            let remainingMinutes = null;
            // 예상 시간이 유효한 숫자일 경우에만 남은 시간 계산
            if (isNumber(item.estimatedMinutes)) {
                remainingMinutes = item.estimatedMinutes - item.totalDurationMinutes;
            }

            // 시간 포맷팅
            const totalFormatted = formatMinutesToDHMS(item.totalDurationMinutes);
            const estimatedFormatted = formatMinutesToDHMS(item.estimatedMinutes);
            const remainingFormatted = formatMinutesToDHMS(remainingMinutes);

            // Priority 포맷팅 (소수점 2자리 또는 '-')
            const priorityFormatted = isFinite(item.priority) && item.priority > -Infinity ? item.priority.toFixed(2) : "-";

            // 테이블 행 생성 (Priority 열 추가)
            // 파이프(|) 문자 이스케이프 처리
            return `| ${item.activity.replace(/\|/g, "\\|")} | ${item.project.replace(/\|/g, "\\|")} | ${item.epic.replace(/\|/g, "\\|")} | ${String(item.impact).replace(/\|/g, "\\|")} | ${priorityFormatted} | ${totalFormatted} | ${estimatedFormatted} | ${remainingFormatted} |`;
        });

        dv.paragraph(header + "\n" + rows.join("\n"));
    } else {
         dv.paragraph("ℹ️ 유효한 활동 그룹이 없습니다 (Task와 매칭된 활동 없음).");
    }
} else {
    dv.paragraph(`ℹ️ 지정된 기간(${startDateRange} ~ ${endDateRange}) 내 '${dailyNoteFolder}' 폴더에서 Task와 매칭되는 활동 로그를 찾지 못했습니다.`);
}

dv.paragraph("🏁 **스크립트 실행 종료**");
logDebug("스크립트 실행 종료.");
// --- SCRIPT END ---

```