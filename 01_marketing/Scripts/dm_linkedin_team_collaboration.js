#!/usr/bin/env node
/**
 * Herramientas de Colaboración en Equipo
 * Asigna recipients, trackea tareas, y genera reportes de equipo
 */
const fs = require('fs');
const path = require('path');

const CONFIG = {
  recipientsFile: path.resolve(__dirname, '../Data_Files/dm_linkedin_recipients.csv'),
  logsFile: path.resolve(__dirname, '../Data_Files/dm_linkedin_logs.csv'),
  assignmentsFile: path.resolve(__dirname, '../Data_Files/dm_linkedin_assignments.csv'),
  outputFile: path.resolve(__dirname, '../Reports/dm_linkedin_team_report.html'),
};

function parseRecipients() {
  if (!fs.existsSync(CONFIG.recipientsFile)) return [];
  const lines = fs.readFileSync(CONFIG.recipientsFile, 'utf8').split('\n').filter(Boolean);
  const headers = lines[0]?.split(',') || [];
  return lines.slice(1).map(l => {
    const parts = l.split(',');
    const obj = {};
    headers.forEach((h, i) => {
      obj[h.trim()] = parts[i]?.trim().replace(/"/g, '') || '';
    });
    return obj;
  });
}

function parseAssignments() {
  if (!fs.existsSync(CONFIG.assignmentsFile)) {
    // Create template
    const header = 'recipient,assigned_to,assigned_date,status,notes';
    fs.writeFileSync(CONFIG.assignmentsFile, header + '\n', 'utf8');
    return [];
  }
  
  const lines = fs.readFileSync(CONFIG.assignmentsFile, 'utf8').split('\n').filter(Boolean);
  const headers = lines[0]?.split(',') || [];
  return lines.slice(1).map(l => {
    const parts = l.split(',');
    const obj = {};
    headers.forEach((h, i) => {
      obj[h.trim()] = parts[i]?.trim().replace(/"/g, '') || '';
    });
    return obj;
  });
}

function assignRecipients(recipients, teamMembers) {
  const assignments = [];
  const memberCounts = {};
  teamMembers.forEach(m => memberCounts[m] = 0);
  
  recipients.forEach((r, idx) => {
    // Round-robin assignment
    const member = teamMembers[idx % teamMembers.length];
    memberCounts[member]++;
    
    assignments.push({
      recipient: r.profileUrl || r.profileurl || '',
      assigned_to: member,
      assigned_date: new Date().toISOString().split('T')[0],
      status: 'pending',
      notes: '',
    });
  });
  
  // Save assignments
  const header = 'recipient,assigned_to,assigned_date,status,notes';
  const rows = assignments.map(a => [
    a.recipient,
    a.assigned_to,
    a.assigned_date,
    a.status,
    a.notes,
  ].join(','));
  
  fs.writeFileSync(CONFIG.assignmentsFile, [header, ...rows].join('\n'), 'utf8');
  
  console.log('✅ Assignments created:');
  teamMembers.forEach(m => {
    console.log(`  ${m}: ${memberCounts[m]} recipients`);
  });
  
  return assignments;
}

function generateTeamReport(assignments, logs) {
  // Stats por miembro
  const stats = {};
  
  assignments.forEach(a => {
    const member = a.assigned_to;
    if (!stats[member]) {
      stats[member] = {
        assigned: 0,
        sent: 0,
        pending: 0,
        completed: 0,
      };
    }
    
    stats[member].assigned++;
    
    if (a.status === 'sent' || a.status === 'completed') {
      stats[member].sent++;
    } else if (a.status === 'pending') {
      stats[member].pending++;
    }
    
    if (a.status === 'completed') {
      stats[member].completed++;
    }
  });
  
  // Logs por miembro (si hay tracking)
  assignments.forEach(a => {
    const sentLogs = logs.filter(l => l.recipient === a.recipient && l.status === 'SENT');
    if (sentLogs.length > 0 && stats[a.assigned_to]) {
      // Ya contado arriba, pero podríamos agregar más métricas
    }
  });
  
  const teamRows = Object.entries(stats)
    .map(([member, data]) => {
      const completionRate = data.assigned > 0 ? (data.completed / data.assigned) * 100 : 0;
      return `<tr>
        <td><strong>${member}</strong></td>
        <td>${data.assigned}</td>
        <td>${data.sent}</td>
        <td>${data.pending}</td>
        <td>${data.completed}</td>
        <td>${completionRate.toFixed(1)}%</td>
      </tr>`;
    })
    .join('');
  
  const html = `<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Team Collaboration Report</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }
    h1 { color: #0077b5; }
    table { width: 100%; border-collapse: collapse; margin: 20px 0; }
    th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
    th { background: #0077b5; color: white; }
    tr:hover { background: #f5f5f5; }
    .summary { background: #f5f7fa; padding: 20px; border-radius: 8px; margin: 20px 0; }
  </style>
</head>
<body>
  <h1>👥 Team Collaboration Report</h1>
  <p>Generated: ${new Date().toLocaleString()}</p>
  
  <div class="summary">
    <h3>📊 Summary</h3>
    <p>Total Assignments: ${assignments.length}</p>
    <p>Team Members: ${Object.keys(stats).length}</p>
  </div>
  
  <h3>📈 Performance by Team Member</h3>
  <table>
    <thead>
      <tr>
        <th>Team Member</th>
        <th>Assigned</th>
        <th>Sent</th>
        <th>Pending</th>
        <th>Completed</th>
        <th>Completion Rate</th>
      </tr>
    </thead>
    <tbody>${teamRows}</tbody>
  </table>
</body>
</html>`;
  
  fs.writeFileSync(CONFIG.outputFile, html, 'utf8');
  console.log(`✅ Team report generated: ${CONFIG.outputFile}`);
}

function main() {
  const action = process.argv[2] || 'report'; // assign, report
  
  if (action === 'assign') {
    const teamMembers = process.argv.slice(3);
    if (teamMembers.length === 0) {
      console.error('❌ Team members required');
      console.log('Usage: node dm_linkedin_team_collaboration.js assign member1 member2 member3');
      return;
    }
    
    const recipients = parseRecipients();
    if (recipients.length === 0) {
      console.warn('⚠️  No recipients found');
      return;
    }
    
    assignRecipients(recipients, teamMembers);
  } else if (action === 'report') {
    const assignments = parseAssignments();
    const logs = [];
    
    if (fs.existsSync(CONFIG.logsFile)) {
      const lines = fs.readFileSync(CONFIG.logsFile, 'utf8').split('\n').filter(Boolean);
      const headers = lines[0]?.split(',') || [];
      logs.push(...lines.slice(1).map(l => {
        const parts = l.split(',');
        const obj = {};
        headers.forEach((h, i) => {
          obj[h.trim()] = parts[i]?.trim().replace(/"/g, '') || '';
        });
        return obj;
      }));
    }
    
    generateTeamReport(assignments, logs);
  }
}

if (require.main === module) {
  main();
}




