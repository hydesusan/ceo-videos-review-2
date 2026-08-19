/**
 * CEO Video Comments — backend for the review page.
 * Deploy this as a Web App:
 *   Extensions → Apps Script → paste this whole file
 *   Deploy → New deployment → Type: Web app
 *   Execute as: Me (susanhyde@berkeley.edu)
 *   Access: Anyone   (← needed so Jennie and Dawn can POST without logging in)
 *   Deploy, authorize, copy the resulting /exec URL
 */

const SHEET_NAME = 'Comments';
const HEADERS = ['id', 'videoId', 'timestamp', 'text', 'reviewer', 'date'];

function getSheet_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName(SHEET_NAME);
  if (!sheet) {
    sheet = ss.insertSheet(SHEET_NAME);
  }
  if (sheet.getLastRow() === 0) {
    sheet.appendRow(HEADERS);
    sheet.setFrozenRows(1);
  }
  return sheet;
}

function doGet(e) {
  const sheet = getSheet_();
  const data = sheet.getDataRange().getValues();
  const rows = data.slice(1).filter(r => r[0]);
  const comments = rows.map(r => ({
    id: r[0],
    videoId: r[1],
    timestamp: Number(r[2]),
    text: r[3],
    reviewer: r[4],
    date: r[5]
  }));
  return ContentService.createTextOutput(JSON.stringify({ ok: true, comments }))
    .setMimeType(ContentService.MimeType.JSON);
}

function doPost(e) {
  let payload;
  try {
    payload = JSON.parse(e.postData.contents);
  } catch (err) {
    return respond_({ ok: false, error: 'invalid JSON' });
  }
  const sheet = getSheet_();

  if (payload.action === 'add') {
    const c = payload.comment || {};
    if (!c.id || !c.videoId || c.timestamp === undefined) {
      return respond_({ ok: false, error: 'missing fields' });
    }
    sheet.appendRow([c.id, c.videoId, c.timestamp, c.text || '', c.reviewer || '', c.date || new Date().toISOString()]);
    return respond_({ ok: true, id: c.id });
  }

  if (payload.action === 'delete') {
    if (!payload.id) return respond_({ ok: false, error: 'missing id' });
    const data = sheet.getDataRange().getValues();
    for (let i = 1; i < data.length; i++) {
      if (data[i][0] === payload.id) {
        sheet.deleteRow(i + 1);
        return respond_({ ok: true });
      }
    }
    return respond_({ ok: false, error: 'not found' });
  }

  if (payload.action === 'bulk_add') {
    const added = [];
    for (const c of (payload.comments || [])) {
      if (c.id && c.videoId && c.timestamp !== undefined) {
        sheet.appendRow([c.id, c.videoId, c.timestamp, c.text || '', c.reviewer || '', c.date || new Date().toISOString()]);
        added.push(c.id);
      }
    }
    return respond_({ ok: true, added });
  }

  return respond_({ ok: false, error: 'unknown action' });
}

function respond_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
