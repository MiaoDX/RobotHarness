#!/usr/bin/env node

/**
 * Agentic Hackathon CLI — AD Hackathon 2026 项目管理命令行工具
 *
 * 单文件、零外部依赖，拷贝即用。
 * 配置文件 config.json 与本脚本同目录。
 *
 * Usage: agentic-hackathon <command> [options]
 */

const http = require('http');
const https = require('https');
const fs = require('fs');
const path = require('path');
const os = require('os');
const { URL } = require('url');

// ─── Config ──────────────────────────────────────────────────────────────────

const CLI_NAME = 'agentic-hackathon';
const CLI_SCRIPT = 'hackathon-ai-cli.js';
const CONFIG_DIR = process.env.AGENTIC_HACKATHON_CONFIG_DIR ||
    path.join(os.homedir(), '.agentic-hackathon');
const CONFIG_PATH = path.join(CONFIG_DIR, 'config.json');
const DEFAULT_SERVER = 'https://agents.evad.mioffice.cn/ad-hackathon-2026/';

function ensureConfigDir() {
    if (!fs.existsSync(CONFIG_DIR)) {
        fs.mkdirSync(CONFIG_DIR, { recursive: true });
    }
}

function readConfigFile(filePath) {
    try {
        if (fs.existsSync(filePath)) {
            return JSON.parse(fs.readFileSync(filePath, 'utf-8'));
        }
    } catch {}
    return null;
}

function loadConfig() {
    const config = readConfigFile(CONFIG_PATH);
    if (config) {
        return config;
    }
    return {};
}

function saveConfig(config) {
    ensureConfigDir();
    fs.writeFileSync(CONFIG_PATH, JSON.stringify(config, null, 2) + '\n', 'utf-8');
}

function normalizeServerBase(server) {
    return String(server || '').trim().replace(/\/+$/, '');
}

function buildApiUrl(server, apiPath) {
    const normalizedServer = normalizeServerBase(server);
    const normalizedPath = apiPath.startsWith('/') ? apiPath : `/${apiPath}`;
    return `${normalizedServer}/api/ai${normalizedPath}`;
}

function getServer(args) {
    return normalizeServerBase(
        args['--server'] ||
        process.env.AGENTIC_HACKATHON_SERVER ||
        loadConfig().server ||
        DEFAULT_SERVER,
    );
}

function getToken(args) {
    return (
        args['--token'] ||
        process.env.AGENTIC_HACKATHON_TOKEN ||
        loadConfig().token ||
        ''
    );
}

// ─── HTTP Client ─────────────────────────────────────────────────────────────

function request(method, urlStr, { token, body, timeout = 15000, headers: extraHeaders = {} } = {}) {
    return new Promise((resolve, reject) => {
        const url = new URL(urlStr);
        const mod = url.protocol === 'https:' ? https : http;
        const headers = {
            'Accept': 'application/json',
            ...extraHeaders,
        };
        if (token && !headers.Authorization) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        let bodyStr;
        if (body !== undefined) {
            bodyStr = JSON.stringify(body);
            headers['Content-Type'] = 'application/json';
            headers['Content-Length'] = Buffer.byteLength(bodyStr);
        }

        const req = mod.request(url, { method, headers, timeout }, (res) => {
            let data = '';
            res.on('data', (chunk) => { data += chunk; });
            res.on('end', () => {
                try {
                    resolve({ status: res.statusCode, data: JSON.parse(data), headers: res.headers, url: url.toString() });
                } catch {
                    resolve({ status: res.statusCode, data: { raw: data }, headers: res.headers, url: url.toString() });
                }
            });
        });

        req.on('error', reject);
        req.on('timeout', () => { req.destroy(); reject(new Error('Request timeout')); });
        if (bodyStr) req.write(bodyStr);
        req.end();
    });
}

async function apiGet(server, path, token) {
    return request('GET', buildApiUrl(server, path), { token });
}

async function apiPost(server, path, token, body, headers) {
    return request('POST', buildApiUrl(server, path), { token, body, headers });
}

async function apiDelete(server, path, token) {
    return request('DELETE', buildApiUrl(server, path), { token });
}

// ─── Formatters ──────────────────────────────────────────────────────────────

function printJson(data) {
    console.log(JSON.stringify(data, null, 2));
}

function printTable(rows, columns) {
    if (!rows || rows.length === 0) {
        console.log('(empty)');
        return;
    }

    // Calculate column widths
    const widths = {};
    for (const col of columns) {
        widths[col.key] = col.label.length;
    }
    for (const row of rows) {
        for (const col of columns) {
            const val = String(row[col.key] ?? '');
            widths[col.key] = Math.max(widths[col.key], val.length);
        }
    }

    // Cap max width
    for (const col of columns) {
        if (col.maxWidth) widths[col.key] = Math.min(widths[col.key], col.maxWidth);
    }

    // Header
    const header = columns.map((c) => c.label.padEnd(widths[c.key])).join('  ');
    console.log(header);
    console.log(columns.map((c) => '─'.repeat(widths[c.key])).join('──'));

    // Rows
    for (const row of rows) {
        const line = columns.map((c) => {
            let val = String(row[c.key] ?? '');
            if (val.length > widths[c.key]) val = val.slice(0, widths[c.key] - 1) + '…';
            return val.padEnd(widths[c.key]);
        }).join('  ');
        console.log(line);
    }
}

function printKV(obj) {
    const maxKeyLen = Math.max(...Object.keys(obj).map((k) => k.length));
    for (const [k, v] of Object.entries(obj)) {
        console.log(`${k.padEnd(maxKeyLen)}  ${v}`);
    }
}

function getCommandRef(command = '') {
    return command ? `${CLI_NAME} ${command}` : CLI_NAME;
}

function getScriptRef(command = '') {
    return command ? `node ${CLI_SCRIPT} ${command}` : `node ${CLI_SCRIPT}`;
}

function getResponseError(res, fallback = '') {
    return (
        res?.data?.error ||
        res?.data?.message ||
        fallback ||
        `HTTP ${res?.status || 'unknown'}`
    );
}

function requireTokenOrExit(token, command = '') {
    if (token) {
        return;
    }

    console.error(`Login required. Use "${getCommandRef('login --token <token>')}" first.`);
    if (command) {
        console.error(`Tried to run: ${getCommandRef(command)}`);
    }
    process.exit(1);
}

function parseList(value) {
    if (Array.isArray(value)) {
        return value.map((item) => String(item || '').trim()).filter(Boolean);
    }

    return String(value || '')
        .split(/[，,、；;\n]/)
        .map((item) => item.trim())
        .filter(Boolean);
}

function maskSecret(value) {
    const raw = String(value || '').trim();
    if (!raw) {
        return '';
    }
    if (raw.length <= 8) {
        return '*'.repeat(raw.length);
    }
    return `${'*'.repeat(Math.max(4, raw.length - 4))}${raw.slice(-4)}`;
}

function resolveProjectId(project = {}) {
    return project.projectId || project.id || '';
}

function formatRole(data = {}) {
    return data.roleLabel || data.identity || data.role || '';
}

async function verifyAuthToken(server, token) {
    const res = await apiGet(server, '/auth/verify', token);
    if ([301, 302, 307, 308].includes(res.status)) {
        console.error('Token verification was redirected by SSO gateway, request did not reach API token validator.');
        console.error(`Request URL: ${res.url}`);
        if (res.headers && res.headers.location) {
            console.error(`Redirect Location: ${res.headers.location}`);
        }
        console.error('Please check server URL/base path and gateway whitelist for Bearer-token API access.');
        process.exit(1);
    }

    if (res.status !== 200 || !res.data?.success) {
        console.error('Token invalid or expired:', getResponseError(res));
        process.exit(1);
    }

    return res.data.data || {};
}

// ─── Arg Parser ──────────────────────────────────────────────────────────────

function parseArgs(argv) {
    const args = { _: [] };
    let i = 0;
    while (i < argv.length) {
        const a = argv[i];
        if (a.startsWith('--')) {
            const next = argv[i + 1];
            if (next && !next.startsWith('--')) {
                args[a] = next;
                i += 2;
            } else {
                args[a] = true;
                i += 1;
            }
        } else {
            args._.push(a);
            i += 1;
        }
    }
    return args;
}

// ─── Commands ────────────────────────────────────────────────────────────────

// --- System ---

async function cmdHealth(server, token, args) {
    const res = await apiGet(server, '/health', token);
    if (args['--json']) return printJson(res.data);
    printKV({ status: res.data.status || 'unknown', timestamp: res.data.timestamp || '' });
}

async function cmdLogin(server, token, args) {
    const t = args['--token'];
    if (!t) {
        console.error(`Usage: ${getCommandRef('login --token <your-token> [--server <url>]')}`);
        console.error(`Or run: ${getScriptRef('login --token <your-token> [--server <url>]')}`);
        process.exit(1);
    }

    const authData = await verifyAuthToken(server, t);
    const config = loadConfig();
    config.token = t;
    config.server = server;
    saveConfig(config);

    if (args['--json']) {
        return printJson({
            success: true,
            server,
            user: authData,
        });
    }

    printKV({
        server,
        username: authData.username || '',
        name: authData.name || '',
        role: formatRole(authData),
    });
    console.log(`\nLogin succeeded. Use "${getCommandRef('auth')}" to check current identity again.`);
}

function cmdLogout() {
    const config = loadConfig();
    delete config.token;
    saveConfig(config);
    console.log('Token cleared.');
}

async function cmdAuth(server, token, args) {
    requireTokenOrExit(token, 'auth');
    const authData = await verifyAuthToken(server, token);
    if (args['--json']) return printJson(authData);
    printKV({
        username: authData.username || '',
        name: authData.name || '',
        email: authData.email || '',
        role: formatRole(authData),
        department: authData.department || '',
    });
}

async function cmdTokenStatus(server, token, args) {
    requireTokenOrExit(token, 'token-status');
    const res = await apiGet(server, '/auth/token', token);
    if (res.status !== 200 || !res.data?.success) {
        console.error('Error:', getResponseError(res));
        process.exit(1);
    }

    const data = res.data.data || {};
    if (args['--json']) return printJson(data);
    printKV({
        hasToken: data.hasToken ? 'yes' : 'no',
        expiresAt: data.expiresAt || '',
        token: data.token ? maskSecret(data.token) : '',
    });
}

async function cmdMe(server, token, args) {
    requireTokenOrExit(token, 'me');
    const res = await apiGet(server, '/projects/users/current', token);
    if (res.status !== 200 || !res.data?.success) {
        console.error('Error:', getResponseError(res));
        process.exit(1);
    }

    const data = res.data.data || {};
    if (args['--json']) return printJson(data);
    printKV({
        username: data.username || '',
        name: data.name || '',
        role: formatRole(data),
        department: data.department || '',
        email: data.email || '',
        canManageAllSubmissions: data.canManageAllSubmissions ? 'yes' : 'no',
    });
}

async function cmdRegistrationAIStatus(server, token, args) {
    requireTokenOrExit(token, 'registration-ai-status');
    const res = await apiGet(server, '/project-registration-ai/status', token);
    if (res.status !== 200 || !res.data?.success) {
        console.error('Error:', getResponseError(res));
        process.exit(1);
    }

    const data = res.data.data || {};
    if (args['--json']) return printJson(data);
    printKV({
        available: data.available ? 'yes' : 'no',
        provider: data.provider || '',
        model: data.model || '',
        latencyMs: data.latencyMs ?? '',
    });
}

// --- Projects ---

async function cmdProjects(server, token, args) {
    requireTokenOrExit(token, 'projects');
    const params = [];
    if (args['--department']) params.push(`department=${encodeURIComponent(args['--department'])}`);
    if (args['--search']) params.push(`search=${encodeURIComponent(args['--search'])}`);
    if (args['--submitter']) params.push(`submitter=${encodeURIComponent(args['--submitter'])}`);
    const qs = params.length ? `?${params.join('&')}` : '';
    const res = await apiGet(server, `/projects${qs}`, token);
    if (res.status !== 200) {
        console.error('Error:', res.data.error || res.data.message || `HTTP ${res.status}`);
        process.exit(1);
    }
    const projects = res.data.data || res.data;
    if (args['--json']) return printJson(projects);
    printTable(
        (Array.isArray(projects) ? projects : []).map((p) => ({
            id: resolveProjectId(p),
            title: p.title || '',
            submitter: p.submitter || '',
            department: p.department || '',
        })),
        [
            { key: 'id', label: 'ID', maxWidth: 6 },
            { key: 'title', label: '项目名称', maxWidth: 40 },
            { key: 'submitter', label: '提交人', maxWidth: 10 },
            { key: 'department', label: '团队', maxWidth: 15 },
        ],
    );
    console.log(`\nTotal: ${Array.isArray(projects) ? projects.length : 0}`);
}

async function cmdProject(server, token, args) {
    requireTokenOrExit(token, 'project');
    const id = args._[1];
    if (!id) {
        console.error(`Usage: ${getCommandRef('project <id>')}`);
        process.exit(1);
    }
    const res = await apiGet(server, `/projects/${encodeURIComponent(id)}`, token);
    if (res.status !== 200) {
        console.error('Error:', res.data.error || `HTTP ${res.status}`);
        process.exit(1);
    }
    const p = res.data.data || res.data;
    if (args['--json']) return printJson(p);
    const tags = Array.isArray(p.tags)
        ? p.tags
        : Array.isArray(p.tagsList)
          ? p.tagsList
          : parseList(p.tags);
    const members = Array.isArray(p.members)
        ? p.members
        : Array.isArray(p.teamMembers)
          ? p.teamMembers.map((m) => m.name || m.username || '')
          : Array.isArray(p.team_members)
            ? p.team_members
            : [];
    printKV({
        ID: resolveProjectId(p),
        标题: p.title || '',
        提交人: p.submitter || '',
        团队: p.department || '',
        描述: p.description || '',
        标签: tags.join(', '),
        成员: members.map((m) => (typeof m === 'string' ? m : m?.name || '')).filter(Boolean).join(', '),
    });
}

async function cmdProjectCreate(server, token, args) {
    requireTokenOrExit(token, 'project-create');

    const contestTracks = parseList(args['--tracks']);
    const teamMembers = parseList(args['--team-members']);
    const tags = parseList(args['--tags']);
    const payload = {
        contestTracks,
        title: args['--title'] || '',
        description: args['--description'] || '',
        registrationSource: 'cli',
        tags,
        teamMembers,
        expectedUsers: args['--expected-users'] || '',
        usageScenarios: args['--usage-scenarios'] || '',
        painPoints: args['--pain-points'] || '',
        industryReference: args['--industry-reference'] || '',
    };

    if (!contestTracks.length || !payload.description || !payload.expectedUsers || !payload.usageScenarios) {
        console.error(`Usage: ${getCommandRef('project-create --tracks 创意赛,应用落地赛 --description "..." --expected-users "..." --usage-scenarios "..." [--title "..."] [--tags Agent,CLI] [--team-members user1,user2] [--pain-points "..."] [--industry-reference "..."]')}`);
        process.exit(1);
    }

    const res = await apiPost(server, '/projects', token, payload, {
        'X-Hackathon-Client': CLI_NAME,
    });
    if (res.status !== 201 || !res.data?.success) {
        console.error('Error:', getResponseError(res));
        process.exit(1);
    }

    if (args['--json']) return printJson(res.data);
    const project = res.data.data || {};
    printKV({
        projectId: resolveProjectId(project),
        title: project.title || '',
        submitter: project.submitter || '',
        department: project.department || '',
    });
}

async function cmdStats(server, token, args) {
    requireTokenOrExit(token, 'stats');
    const res = await apiGet(server, '/projects/stats/all', token);
    if (res.status !== 200) {
        console.error('Error:', res.data.error || `HTTP ${res.status}`);
        process.exit(1);
    }
    const s = res.data;
    if (args['--json']) return printJson(s);
    printKV({
        项目总数: s.totalProjects || 0,
        参与人数: s.totalUsers || 0,
        参与团队: s.totalDepartments || 0,
    });
}

async function cmdAiReviewScores(server, token, args) {
    requireTokenOrExit(token, 'ai-review-scores');
    const res = await apiGet(server, '/projects/ai-reviews/scores', token);
    if (res.status !== 200 || !res.data?.success) {
        console.error('Error:', getResponseError(res));
        process.exit(1);
    }

    const data = res.data.data || {};
    if (args['--json']) return printJson(data);
    const rows = Object.entries(data).map(([projectId, scoreData]) => ({
        projectId,
        averageScore: scoreData.averageScore ?? 0,
        totalReviews: scoreData.totalReviews ?? 0,
    }));
    printTable(rows, [
        { key: 'projectId', label: 'ID', maxWidth: 8 },
        { key: 'averageScore', label: '平均分' },
        { key: 'totalReviews', label: '次数' },
    ]);
}

async function cmdProjectAIReview(server, token, args) {
    requireTokenOrExit(token, 'ai-review');
    const id = args._[1];
    if (!id) {
        console.error(`Usage: ${getCommandRef('ai-review <projectId>')}`);
        process.exit(1);
    }

    const res = await apiGet(server, `/projects/${encodeURIComponent(id)}/ai-review`, token);
    if (res.status !== 200 || !res.data?.success) {
        console.error('Error:', getResponseError(res));
        process.exit(1);
    }

    const data = res.data.data;
    if (args['--json']) return printJson(data);
    if (!data) {
        console.log(`Project ${id}: no AI review.`);
        return;
    }

    printKV({
        projectId: data.projectId || id,
        averageScore: data.averageScore ?? 0,
        totalReviews: data.totalReviews ?? 0,
        updatedAt: data.updatedAt || '',
    });

    const reviews = Array.isArray(data.reviews) ? data.reviews : [];
    if (reviews.length) {
        console.log('');
        reviews.forEach((review, index) => {
            console.log(`#${index + 1} [${review.score}] ${review.model || 'unknown-model'} ${review.createdAt || ''}`);
            console.log(review.comment || '');
            console.log('');
        });
    }
}

async function cmdUsers(server, token, args) {
    requireTokenOrExit(token, 'users');
    const res = await apiGet(server, '/projects/users/list', token);
    if (res.status !== 200) {
        console.error('Error:', res.data.error || `HTTP ${res.status}`);
        process.exit(1);
    }
    const users = res.data.data || [];
    if (args['--json']) return printJson(users);
    printTable(
        users.map((u) => ({
            name: u.name || '',
            projects: u.projectCount || u.projects || 0,
        })),
        [
            { key: 'name', label: '姓名', maxWidth: 20 },
            { key: 'projects', label: '项目数' },
        ],
    );
    console.log(`\nTotal: ${users.length}`);
}

async function cmdDepartments(server, token, args) {
    requireTokenOrExit(token, 'departments');
    const res = await apiGet(server, '/projects/departments/list', token);
    if (res.status !== 200) {
        console.error('Error:', res.data.error || `HTTP ${res.status}`);
        process.exit(1);
    }
    const depts = res.data.data || [];
    if (args['--json']) return printJson(depts);
    printTable(
        depts.map((d) => ({
            name: d.name || '',
            projects: d.projectCount || d.projects || 0,
        })),
        [
            { key: 'name', label: '团队', maxWidth: 20 },
            { key: 'projects', label: '项目数' },
        ],
    );
    console.log(`\nTotal: ${depts.length}`);
}

// --- Comments ---

async function cmdCommentsStats(server, token, args) {
    requireTokenOrExit(token, 'comments-stats');
    const res = await apiGet(server, '/comments/stats/all', token);
    if (res.status !== 200 || !res.data?.success) {
        console.error('Error:', getResponseError(res));
        process.exit(1);
    }

    const data = res.data.data || {};
    if (args['--json']) return printJson(data);
    const rows = Object.entries(data).map(([projectId, count]) => ({
        projectId,
        count,
    }));
    printTable(rows, [
        { key: 'projectId', label: 'ID', maxWidth: 8 },
        { key: 'count', label: '评论节点数' },
    ]);
}

async function cmdComments(server, token, args) {
    requireTokenOrExit(token, 'comments');
    const id = args._[1];
    if (!id) {
        console.error(`Usage: ${getCommandRef('comments <id>')}`);
        process.exit(1);
    }
    const res = await apiGet(server, `/comments/${encodeURIComponent(id)}`, token);
    if (res.status !== 200) {
        console.error('Error:', res.data.error || `HTTP ${res.status}`);
        process.exit(1);
    }
    if (args['--json']) return printJson(res.data.data || res.data);
    const d = res.data.data || {};
    const comments = d.comments || [];
    if (comments.length === 0) {
        console.log('No comments.');
        return;
    }
    for (const c of comments) {
        printComment(c, 0);
    }
    console.log(`\nTotal: ${d.stats?.totalNodes || comments.length}`);
}

function printComment(comment, depth) {
    const indent = '  '.repeat(depth);
    const author = typeof comment.author === 'string'
        ? comment.author
        : comment.author?.name || comment.author?.username || 'anonymous';
    const time = comment.createdAt ? new Date(comment.createdAt).toLocaleString() : '';
    const deleted = comment.deleted ? ' [已删除]' : '';
    console.log(`${indent}[${comment.id || '?'}] ${author} (${time})${deleted}`);
    if (!comment.deleted) {
        console.log(`${indent}  ${comment.content || ''}`);
    }
    if (comment.replies) {
        for (const r of comment.replies) {
            printComment(r, depth + 1);
        }
    }
}

async function cmdComment(server, token, args) {
    const id = args._[1];
    const content = args['--content'];
    if (!id || !content) {
        console.error(`Usage: ${getCommandRef('comment <id> --content "内容" [--reply <parentId>]')}`);
        process.exit(1);
    }
    requireTokenOrExit(token, 'comment');
    const body = { content };
    if (args['--reply']) body.parentId = args['--reply'];
    const res = await apiPost(server, `/comments/${encodeURIComponent(id)}`, token, body);
    if (res.status !== 200 && res.status !== 201) {
        console.error('Error:', res.data.error || res.data.message || `HTTP ${res.status}`);
        process.exit(1);
    }
    if (args['--json']) return printJson(res.data);
    console.log('Comment posted:', res.data.data?.comment?.id || 'ok');
}

async function cmdCommentDelete(server, token, args) {
    const projectId = args._[1];
    const commentId = args._[2];
    if (!projectId || !commentId) {
        console.error(`Usage: ${getCommandRef('comment-delete <projectId> <commentId>')}`);
        process.exit(1);
    }
    requireTokenOrExit(token, 'comment-delete');
    const res = await apiDelete(server, `/comments/${encodeURIComponent(projectId)}/${encodeURIComponent(commentId)}`, token);
    if (res.status !== 200) {
        console.error('Error:', res.data.error || res.data.message || `HTTP ${res.status}`);
        process.exit(1);
    }
    if (args['--json']) return printJson(res.data);
    console.log('Comment deleted:', commentId);
}

// --- Submissions ---

async function cmdSubmissions(server, token, args) {
    requireTokenOrExit(token, 'submissions');
    const res = await apiGet(server, '/submissions', token);
    if (res.status !== 200) {
        console.error('Error:', res.data.error || `HTTP ${res.status}`);
        process.exit(1);
    }
    const subs = res.data.data || [];
    if (args['--json']) return printJson(subs);
    printTable(
        subs.map((s) => ({
            projectId: s.projectId || '',
            submitted: (s.documentUrl || s.gitRepository || s.videoUrl) ? '✓' : '✗',
            documentUrl: s.documentUrl || '',
            gitRepository: s.gitRepository ? '✓' : '',
            videoUrl: s.videoUrl ? '✓' : '',
        })),
        [
            { key: 'projectId', label: 'ID', maxWidth: 6 },
            { key: 'submitted', label: '状态' },
            { key: 'documentUrl', label: '文档链接', maxWidth: 50 },
            { key: 'gitRepository', label: 'Git' },
            { key: 'videoUrl', label: '视频' },
        ],
    );
    console.log(`\nTotal: ${subs.length}`);
}

async function cmdSubmission(server, token, args) {
    requireTokenOrExit(token, 'submission');
    const id = args._[1];
    if (!id) {
        console.error(`Usage: ${getCommandRef('submission <id>')}`);
        process.exit(1);
    }
    const res = await apiGet(server, `/submissions/${encodeURIComponent(id)}`, token);
    if (res.status !== 200) {
        console.error('Error:', res.data.error || `HTTP ${res.status}`);
        process.exit(1);
    }
    if (args['--json']) return printJson(res.data);
    const d = res.data;
    if (!d.submitted) {
        console.log(`Project ${id}: not submitted`);
        return;
    }
    printKV({
        项目: d.data?.projectId || id,
        文档链接: d.data?.documentUrl || '',
        Git仓库: d.data?.gitRepository || '',
        GitToken: d.data?.gitAccessToken ? maskSecret(d.data.gitAccessToken) : '',
        视频: d.data?.videoUrl ? '✓' : '✗',
        提交时间: d.data?.submittedAt || '',
    });
}

async function cmdSubmit(server, token, args) {
    const id = args._[1];
    const doc = args['--doc'];
    const git = args['--git'];
    const gitAccessToken = args['--git-access-token'];
    if (!id || (!doc && !git)) {
        console.error(`Usage: ${getCommandRef('submit <id> [--doc <url>] [--git <repo>] [--git-access-token <token>] [--audience <text>] [--scenarios <text>] [--painpoints <text>]')}`);
        process.exit(1);
    }
    requireTokenOrExit(token, 'submit');

    // Note: video upload requires multipart/form-data file handling and is not supported in this simple CLI.
    // Use the web interface for video uploads.
    const boundary = '----HackathonCLI' + Date.now();
    const fields = {};
    if (doc) fields.documentUrl = doc;
    if (git) fields.gitRepository = git;
    if (gitAccessToken) fields.gitAccessToken = gitAccessToken;
    if (args['--audience']) fields.targetAudience = args['--audience'];
    if (args['--scenarios']) fields.usageScenarios = args['--scenarios'];
    if (args['--painpoints']) fields.painPoints = args['--painpoints'];

    if (Object.keys(fields).length === 0) {
        console.error(`Usage: ${getCommandRef('submit <id> [--doc <url>] [--git <repo>] [--git-access-token <token>]')}`);
        process.exit(1);
    }

    let bodyParts = [];
    for (const [key, val] of Object.entries(fields)) {
        bodyParts.push(`--${boundary}\r\nContent-Disposition: form-data; name="${key}"\r\n\r\n${val}`);
    }
    const bodyStr = bodyParts.join('\r\n') + `\r\n--${boundary}--\r\n`;

    const url = new URL(`${server}/api/ai/submissions/${encodeURIComponent(id)}`);
    const mod = url.protocol === 'https:' ? https : http;

    const res = await new Promise((resolve, reject) => {
        const req = mod.request(url, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': `multipart/form-data; boundary=${boundary}`,
                'Content-Length': Buffer.byteLength(bodyStr),
            },
        }, (res) => {
            let data = '';
            res.on('data', (chunk) => { data += chunk; });
            res.on('end', () => {
                try { resolve({ status: res.statusCode, data: JSON.parse(data) }); }
                catch { resolve({ status: res.statusCode, data: { raw: data } }); }
            });
        });
        req.on('error', reject);
        req.write(bodyStr);
        req.end();
    });

    if (res.status !== 200) {
        console.error('Error:', res.data.error || res.data.message || `HTTP ${res.status}`);
        process.exit(1);
    }
    if (args['--json']) return printJson(res.data);
    console.log('Submitted:', id);
}

async function cmdSubmissionDelete(server, token, args) {
    const id = args._[1];
    if (!id) {
        console.error(`Usage: ${getCommandRef('submission-delete <id>')}`);
        process.exit(1);
    }
    requireTokenOrExit(token, 'submission-delete');
    const res = await apiDelete(server, `/submissions/${encodeURIComponent(id)}`, token);
    if (res.status !== 200) {
        console.error('Error:', res.data.error || res.data.message || `HTTP ${res.status}`);
        process.exit(1);
    }
    if (args['--json']) return printJson(res.data);
    console.log('Submission deleted:', id);
}

// --- Interactions ---

async function cmdInteraction(server, token, args) {
    requireTokenOrExit(token, 'interaction');
    const projectId = args._[1];
    if (!projectId) {
        console.error(`Usage: ${getCommandRef('interaction <projectId>')}`);
        process.exit(1);
    }

    const res = await apiGet(server, `/interactions/projects/${encodeURIComponent(projectId)}`, token);
    if (res.status !== 200 || !res.data?.success) {
        console.error('Error:', getResponseError(res));
        process.exit(1);
    }

    const data = res.data.data || {};
    if (args['--json']) return printJson(data);
    printKV({
        projectId: data.projectId || projectId,
        publicReviewVisible: data.publicReview?.visible ? 'yes' : 'no',
        publicReviewSelected: data.publicReview?.isSelected ? 'yes' : 'no',
        publicReviewCount: data.publicReview?.totalCount ?? 0,
        publicReviewRemaining: data.publicReview?.remaining ?? 0,
        expectationSelected: data.expectation?.isSelected ? 'yes' : 'no',
        expectationCount: data.expectation?.totalCount ?? 0,
    });
}

async function cmdInteractionStats(server, token, args) {
    requireTokenOrExit(token, 'interaction-stats');
    const res = await apiGet(server, '/interactions/stats', token);
    if (res.status !== 200 || !res.data?.success) {
        console.error('Error:', getResponseError(res));
        process.exit(1);
    }

    const data = res.data.data || {};
    if (args['--json']) return printJson(data);
    printKV({
        totalReviewers: data.totalReviewers ?? 0,
    });
}

async function cmdInteractionCounts(server, token, args) {
    requireTokenOrExit(token, 'interaction-counts');
    const res = await apiGet(server, '/interactions/counts', token);
    if (res.status !== 200 || !res.data?.success) {
        console.error('Error:', getResponseError(res));
        process.exit(1);
    }

    const data = res.data.data || {};
    if (args['--json']) return printJson(data);
    const rows = Object.entries(data).map(([projectId, countData]) => ({
        projectId,
        publicReviewCount: countData.publicReviewCount ?? 0,
        expectationCount: countData.expectationCount ?? 0,
    }));
    printTable(rows, [
        { key: 'projectId', label: 'ID', maxWidth: 8 },
        { key: 'publicReviewCount', label: '大众评审' },
        { key: 'expectationCount', label: '期待' },
    ]);
}

async function cmdReviewers(server, token, args) {
    requireTokenOrExit(token, 'reviewers');
    const res = await apiGet(server, '/interactions/reviewers', token);
    if (res.status !== 200 || !res.data?.success) {
        console.error('Error:', getResponseError(res));
        process.exit(1);
    }

    const data = res.data.data || {};
    const reviewers = Array.isArray(data.reviewers) ? data.reviewers : [];
    if (args['--json']) return printJson(data);
    printTable(
        reviewers.map((reviewer) => ({
            username: reviewer.username || '',
            name: reviewer.name || '',
            department: reviewer.department || '',
            used: reviewer.used ?? 0,
            remaining: reviewer.remaining ?? 0,
            limit: reviewer.limit ?? data.limit ?? 0,
        })),
        [
            { key: 'username', label: '用户名', maxWidth: 20 },
            { key: 'name', label: '姓名', maxWidth: 20 },
            { key: 'department', label: '团队', maxWidth: 20 },
            { key: 'used', label: '已用' },
            { key: 'remaining', label: '剩余' },
            { key: 'limit', label: '上限' },
        ],
    );
}

// --- Judges ---

async function cmdJudgeCheck(server, token, args) {
    requireTokenOrExit(token, 'judge check');
    const res = await apiGet(server, '/judges/check', token);
    if (res.status !== 200) {
        console.error('Error:', getResponseError(res));
        process.exit(1);
    }
    if (args['--json']) return printJson(res.data);
    printKV({
        isJudge: res.data.isJudge ? 'yes' : 'no',
        role: res.data.roleLabel || res.data.identity || '',
        judgeUsername: res.data.judge?.username || '',
        judgeName: res.data.judge?.name || '',
    });
}

async function cmdJudgeScoreConfig(server, token, args) {
    requireTokenOrExit(token, 'judge score-config');
    const res = await apiGet(server, '/judges/score-config', token);
    if (res.status !== 200 || !res.data?.success) {
        console.error('Error:', getResponseError(res));
        process.exit(1);
    }

    if (args['--json']) return printJson(res.data.data);
    const config = res.data.data || {};
    const categories = Array.isArray(config.categories) ? config.categories : [];
    printKV({
        version: config.version || '',
        updatedAt: config.updatedAt || '',
        categories: categories.length,
    });
    console.log('');
    categories.forEach((category) => {
        console.log(`[${category.id}] ${category.name}`);
        (category.items || []).forEach((item) => {
            console.log(`  - ${item.id}: ${item.name} (${item.min}-${item.max})${item.required ? ' [required]' : ''}`);
        });
    });
}

async function cmdJudgeProjects(server, token, args) {
    requireTokenOrExit(token, 'judge projects');
    const res = await apiGet(server, '/judges/projects', token);
    if (res.status !== 200) {
        console.error('Error:', getResponseError(res));
        process.exit(1);
    }
    const projects = res.data.data || [];
    if (args['--json']) return printJson(projects);
    printTable(
        projects.map((p) => ({
            id: p.projectId || p.id || '',
            title: p.title || '',
            status: p.scoreStatus || '',
            score: p.totalScore ?? '',
        })),
        [
            { key: 'id', label: 'ID', maxWidth: 6 },
            { key: 'title', label: '项目名称', maxWidth: 40 },
            { key: 'status', label: '评分状态', maxWidth: 10 },
            { key: 'score', label: '分数' },
        ],
    );
    const stats = res.data.stats || {};
    console.log(`\nCompleted: ${stats.completed || 0}  In Progress: ${stats.inProgress || 0}  Not Started: ${stats.notStarted || 0}`);
}

async function cmdJudgeProject(server, token, args) {
    const id = args._[2];
    if (!id) {
        console.error(`Usage: ${getCommandRef('judge project <id>')}`);
        process.exit(1);
    }
    requireTokenOrExit(token, 'judge project');
    const res = await apiGet(server, `/judges/projects/${encodeURIComponent(id)}`, token);
    if (res.status !== 200) {
        console.error('Error:', getResponseError(res));
        process.exit(1);
    }
    if (args['--json']) return printJson(res.data.data);
    const d = res.data.data || {};
    const p = d.project || {};
    const sub = d.submission || {};
    const score = d.myScore || {};
    printKV({
        ID: resolveProjectId(p),
        标题: p.title || '',
        提交人: p.submitter || '',
        文档: sub.documentUrl || '(未提交)',
        视频: sub.videoUrl ? '✓' : '✗',
        我的评分: score.totalScore ?? '(未评)',
        评分状态: score.status || '(未评)',
    });
}

async function cmdJudgeScore(server, token, args) {
    const id = args._[2];
    const scoresStr = args['--scores'];
    if (!id || !scoresStr) {
        console.error(`Usage: ${getCommandRef(`judge score <id> --scores '{"category":{"item":7}}' [--comment "评语"] [--status in_progress|completed]`)}`);
        process.exit(1);
    }
    requireTokenOrExit(token, 'judge score');
    let scores;
    try { scores = JSON.parse(scoresStr); } catch {
        console.error('Invalid JSON for --scores');
        process.exit(1);
    }
    const body = { scores };
    if (args['--comment']) body.comment = args['--comment'];
    if (args['--status']) body.status = args['--status'];
    const res = await apiPost(server, `/judges/scores/${encodeURIComponent(id)}`, token, body);
    if (res.status !== 200) {
        console.error('Error:', getResponseError(res));
        process.exit(1);
    }
    if (args['--json']) return printJson(res.data);
    console.log(`Score saved for ${id}: ${res.data.data?.totalScore ?? 'ok'}`);
}

async function cmdJudgeMyScores(server, token, args) {
    requireTokenOrExit(token, 'judge my-scores');
    const res = await apiGet(server, '/judges/scores/my', token);
    if (res.status !== 200) {
        console.error('Error:', getResponseError(res));
        process.exit(1);
    }
    const scores = res.data.data || [];
    if (args['--json']) return printJson(scores);
    printTable(
        scores.map((s) => ({
            projectId: s.projectId || '',
            total: s.totalScore ?? '',
            status: s.status || '',
        })),
        [
            { key: 'projectId', label: 'ID', maxWidth: 6 },
            { key: 'total', label: '总分' },
            { key: 'status', label: '状态' },
        ],
    );
}

async function cmdJudgeAIReview(server, token, args) {
    const id = args._[2];
    if (!id) {
        console.error(`Usage: ${getCommandRef('judge ai-review <projectId>')}`);
        process.exit(1);
    }
    requireTokenOrExit(token, 'judge ai-review');

    const res = await apiGet(server, `/judges/ai-review/${encodeURIComponent(id)}`, token);
    if (res.status !== 200 || !res.data?.success) {
        console.error('Error:', getResponseError(res));
        process.exit(1);
    }

    const data = res.data.data;
    if (args['--json']) return printJson(data);
    if (!data) {
        console.log(`Project ${id}: no judge AI review.`);
        return;
    }

    printKV({
        projectId: data.projectId || id,
        averageScore: data.averageScore ?? 0,
        totalReviews: data.totalReviews ?? 0,
        updatedAt: data.updatedAt || '',
    });
    console.log('');
    (data.reviews || []).forEach((review, index) => {
        printKV({
            [`#${index + 1} id`]: review.id || '',
            score: review.score ?? '',
            model: review.model || '',
            mcpServer: review.mcpServer || '',
            createdAt: review.createdAt || '',
            comment: review.comment || '',
        });
        console.log('');
    });
}

async function cmdJudgeAISubmit(server, token, args) {
    const id = args._[2];
    const score = args['--score'];
    const comment = args['--comment'];
    if (!id || score === undefined || !comment) {
        console.error(`Usage: ${getCommandRef('judge ai-submit <projectId> --score <1-7> --comment "评语" [--model <model>] [--mcp-server <name>]')}`);
        process.exit(1);
    }
    requireTokenOrExit(token, 'judge ai-submit');

    const body = {
        score: Number(score),
        comment,
    };
    if (args['--model']) body.model = args['--model'];
    if (args['--mcp-server']) body.mcpServer = args['--mcp-server'];

    const res = await apiPost(server, `/judges/ai-review/${encodeURIComponent(id)}`, token, body);
    if (res.status !== 201 || !res.data?.success) {
        console.error('Error:', getResponseError(res));
        process.exit(1);
    }

    if (args['--json']) return printJson(res.data);
    printKV({
        projectId: res.data.data?.projectId || id,
        reviewId: res.data.data?.review?.id || '',
        averageScore: res.data.data?.averageScore ?? '',
        totalReviews: res.data.data?.totalReviews ?? '',
    });
}

async function cmdJudgeAIDelete(server, token, args) {
    const projectId = args._[2];
    const reviewId = args._[3];
    if (!projectId || !reviewId) {
        console.error(`Usage: ${getCommandRef('judge ai-delete <projectId> <reviewId>')}`);
        process.exit(1);
    }
    requireTokenOrExit(token, 'judge ai-delete');

    const res = await apiDelete(server, `/judges/ai-review/${encodeURIComponent(projectId)}/${encodeURIComponent(reviewId)}`, token);
    if (res.status !== 200 || !res.data?.success) {
        console.error('Error:', getResponseError(res));
        process.exit(1);
    }

    if (args['--json']) return printJson(res.data);
    printKV({
        projectId,
        reviewId,
        remainingReviews: res.data.data?.remainingReviews ?? 0,
        averageScore: res.data.data?.averageScore ?? 0,
    });
}

async function cmdJudgeRankings(server, token, args) {
    requireTokenOrExit(token, 'judge rankings');
    const res = await apiGet(server, '/judges/rankings', token);
    if (res.status !== 200) {
        console.error('Error:', getResponseError(res));
        process.exit(1);
    }
    if (args['--json']) return printJson(res.data.data);
    const awards = res.data.data?.awards || [];
    for (const award of awards) {
        console.log(`\n=== ${award.name || award.type || 'Award'} ===`);
        const projects = award.projects || award.rankings || [];
        printTable(
            projects.map((p, i) => ({
                rank: i + 1,
                id: p.projectId || p.id || '',
                title: p.title || '',
                score: p.score ?? p.totalScore ?? '',
            })),
            [
                { key: 'rank', label: '#' },
                { key: 'id', label: 'ID', maxWidth: 6 },
                { key: 'title', label: '项目名称', maxWidth: 40 },
                { key: 'score', label: '分数' },
            ],
        );
    }
}

// ─── Help ────────────────────────────────────────────────────────────────────

function printHelp() {
    console.log(`Agentic Hackathon CLI — AD Hackathon 2026

Preferred command:
  ${CLI_NAME} <command> [options]

Direct script:
  ${getScriptRef('<command> [options]')}

Global Options:
  --server <url>     Server URL (default: ${DEFAULT_SERVER})
  --token <token>    API Token
  --json             Output raw JSON
  --help             Show this help

Environment Variables:
  AGENTIC_HACKATHON_SERVER
  AGENTIC_HACKATHON_TOKEN

[GET] System:
  health                                  GET /api/ai/health
  auth                                    GET /api/ai/auth/verify
  token-status                            GET /api/ai/auth/token
  me                                      GET /api/ai/projects/users/current
  registration-ai-status                  GET /api/ai/project-registration-ai/status

[GET] Projects:
  projects [--search X] [--department X] [--submitter X]   GET /api/ai/projects
  project <id>                                             GET /api/ai/projects/:id
  stats                                                    GET /api/ai/projects/stats/all
  users                                                    GET /api/ai/projects/users/list
  departments                                              GET /api/ai/projects/departments/list
  ai-review-scores                                         GET /api/ai/projects/ai-reviews/scores
  ai-review <projectId>                                    GET /api/ai/projects/:id/ai-review

[GET] Comments:
  comments-stats                                            GET /api/ai/comments/stats/all
  comments <projectId>                                      GET /api/ai/comments/:projectId

[GET] Submissions:
  submissions                                               GET /api/ai/submissions
  submission <projectId>                                    GET /api/ai/submissions/:projectId

[GET] Interactions:
  interaction <projectId>                                   GET /api/ai/interactions/projects/:projectId
  interaction-stats                                         GET /api/ai/interactions/stats
  interaction-counts                                        GET /api/ai/interactions/counts
  reviewers                                                 GET /api/ai/interactions/reviewers

[GET] Judges:
  judge check                                               GET /api/ai/judges/check
  judge score-config                                        GET /api/ai/judges/score-config
  judge projects                                            GET /api/ai/judges/projects
  judge project <id>                                        GET /api/ai/judges/projects/:projectId
  judge my-scores                                           GET /api/ai/judges/scores/my
  judge ai-review <projectId>                               GET /api/ai/judges/ai-review/:projectId
  judge rankings                                            GET /api/ai/judges/rankings

[WRITE] Auth / Project / Comment / Submission:
  login --token <token> [--server <url>]                    Verify token and save local config
  logout                                                    Clear saved token
  project-create --tracks ... --description ... --expected-users ... --usage-scenarios ...
  comment <projectId> --content "text" [--reply <parentId>]
  comment-delete <projectId> <commentId>
  submit <projectId> [--doc <url>] [--git <repo>] [--git-access-token <token>]
  submission-delete <projectId>

[WRITE] Judges:
  judge score <id> --scores '{"category":{"item":7}}' [--comment "text"] [--status in_progress|completed]
  judge ai-submit <projectId> --score <1-7> --comment "评语" [--model <model>] [--mcp-server <name>]
  judge ai-delete <projectId> <reviewId>
`);
}

// ─── Main ────────────────────────────────────────────────────────────────────

async function main() {
    const args = parseArgs(process.argv.slice(2));
    const cmd = args._[0];

    if (!cmd || args['--help']) {
        printHelp();
        return;
    }

    const server = getServer(args);
    const token = getToken(args);

    try {
        switch (cmd) {
            case 'health':            return await cmdHealth(server, token, args);
            case 'login':             return await cmdLogin(server, token, args);
            case 'logout':            return cmdLogout();
            case 'auth':              return await cmdAuth(server, token, args);
            case 'token-status':      return await cmdTokenStatus(server, token, args);
            case 'me':                return await cmdMe(server, token, args);
            case 'registration-ai-status':
                return await cmdRegistrationAIStatus(server, token, args);
            case 'projects':          return await cmdProjects(server, token, args);
            case 'project':           return await cmdProject(server, token, args);
            case 'project-create':    return await cmdProjectCreate(server, token, args);
            case 'stats':             return await cmdStats(server, token, args);
            case 'ai-review-scores':  return await cmdAiReviewScores(server, token, args);
            case 'ai-review':         return await cmdProjectAIReview(server, token, args);
            case 'users':             return await cmdUsers(server, token, args);
            case 'departments':       return await cmdDepartments(server, token, args);
            case 'comments-stats':    return await cmdCommentsStats(server, token, args);
            case 'comments':          return await cmdComments(server, token, args);
            case 'comment':           return await cmdComment(server, token, args);
            case 'comment-delete':    return await cmdCommentDelete(server, token, args);
            case 'submissions':       return await cmdSubmissions(server, token, args);
            case 'submission':        return await cmdSubmission(server, token, args);
            case 'submit':            return await cmdSubmit(server, token, args);
            case 'submission-delete': return await cmdSubmissionDelete(server, token, args);
            case 'interaction':       return await cmdInteraction(server, token, args);
            case 'interaction-stats': return await cmdInteractionStats(server, token, args);
            case 'interaction-counts':return await cmdInteractionCounts(server, token, args);
            case 'reviewers':         return await cmdReviewers(server, token, args);
            case 'judge':
                switch (args._[1]) {
                    case 'check':     return await cmdJudgeCheck(server, token, args);
                    case 'score-config':
                        return await cmdJudgeScoreConfig(server, token, args);
                    case 'projects':  return await cmdJudgeProjects(server, token, args);
                    case 'project':   return await cmdJudgeProject(server, token, args);
                    case 'score':     return await cmdJudgeScore(server, token, args);
                    case 'my-scores': return await cmdJudgeMyScores(server, token, args);
                    case 'ai-review': return await cmdJudgeAIReview(server, token, args);
                    case 'ai-submit': return await cmdJudgeAISubmit(server, token, args);
                    case 'ai-delete': return await cmdJudgeAIDelete(server, token, args);
                    case 'rankings':  return await cmdJudgeRankings(server, token, args);
                    default:
                        console.error('Unknown judge subcommand. Use --help for usage.');
                        process.exit(1);
                }
                break;
            default:
                console.error(`Unknown command: ${cmd}. Use --help for usage.`);
                process.exit(1);
        }
    } catch (err) {
        console.error('Error:', err.message || err);
        process.exit(1);
    }
}

main();
