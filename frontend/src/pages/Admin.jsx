import { useCallback, useEffect, useId, useMemo, useState } from 'react'
import AppLayout from '../components/layout/AppLayout'
import BarList from '../components/admin/BarList'
import StatCard from '../components/admin/StatCard'
import Badge from '../components/ui/Badge'
import Button from '../components/ui/Button'
import Card from '../components/ui/Card'
import EmptyState from '../components/ui/EmptyState'
import ProgressBar from '../components/ui/ProgressBar'
import { api } from '../lib/api'
import { useFocusTrap } from '../hooks/useFocusTrap'
import { FOCUS_RING } from '../lib/focusStyles'

const SECTIONS = [
  { id: 'overview', label: 'Overview' },
  { id: 'reliability', label: 'Reliability' },
  { id: 'reports', label: 'Question Reports' },
  { id: 'feedback', label: 'Student Feedback' },
  { id: 'analytics', label: 'Platform Analytics' },
  { id: 'health', label: 'Database Health' },
  { id: 'impact', label: 'Impact Overview' },
]

const REPORT_REASON_OPTIONS = [
  { value: 'all', label: 'All reasons' },
  { value: 'incorrect_answer', label: 'Wrong answer' },
  { value: 'confusing_wording', label: 'Confusing wording' },
  { value: 'wrong_explanation', label: 'Wrong explanation' },
  { value: 'other', label: 'Other' },
]

function reasonLabel(reason) {
  return (
    REPORT_REASON_OPTIONS.find((o) => o.value === reason)?.label || reason || '—'
  )
}

function formatDate(value) {
  if (!value) return '—'
  try {
    return new Date(value).toLocaleString()
  } catch {
    return String(value)
  }
}

function statusTone(status) {
  if (status === 'resolved') return 'green'
  if (status === 'ignored') return 'amber'
  return 'blue'
}

function SectionNav({ active, onChange }) {
  return (
    <div
      role="tablist"
      aria-label="Admin sections"
      className="flex flex-wrap gap-2"
    >
      {SECTIONS.map((section) => {
        const isActive = active === section.id
        return (
          <button
            key={section.id}
            type="button"
            role="tab"
            id={`admin-tab-${section.id}`}
            aria-selected={isActive}
            aria-controls={`admin-panel-${section.id}`}
            tabIndex={isActive ? 0 : -1}
            onClick={() => onChange(section.id)}
            onKeyDown={(event) => {
              const idx = SECTIONS.findIndex((s) => s.id === active)
              if (event.key === 'ArrowRight' || event.key === 'ArrowDown') {
                event.preventDefault()
                const next = SECTIONS[(idx + 1) % SECTIONS.length]
                onChange(next.id)
                requestAnimationFrame(() =>
                  document.getElementById(`admin-tab-${next.id}`)?.focus(),
                )
              } else if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') {
                event.preventDefault()
                const prev = SECTIONS[(idx - 1 + SECTIONS.length) % SECTIONS.length]
                onChange(prev.id)
                requestAnimationFrame(() =>
                  document.getElementById(`admin-tab-${prev.id}`)?.focus(),
                )
              } else if (event.key === 'Home') {
                event.preventDefault()
                onChange(SECTIONS[0].id)
                requestAnimationFrame(() =>
                  document.getElementById(`admin-tab-${SECTIONS[0].id}`)?.focus(),
                )
              } else if (event.key === 'End') {
                event.preventDefault()
                const last = SECTIONS[SECTIONS.length - 1]
                onChange(last.id)
                requestAnimationFrame(() =>
                  document.getElementById(`admin-tab-${last.id}`)?.focus(),
                )
              }
            }}
            className={[
              'min-h-10 rounded-md px-3 py-2 text-sm font-medium',
              FOCUS_RING,
              isActive
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-800 hover:bg-gray-200',
            ].join(' ')}
          >
            {section.label}
          </button>
        )
      })}
    </div>
  )
}

function LoadingBlock() {
  return (
    <p className="text-sm text-gray-600" role="status" aria-live="polite">
      Loading…
    </p>
  )
}

function OverviewSection({ data }) {
  if (!data) return <LoadingBlock />

  const cards = [
    { label: 'Registered users', value: data.registered_users },
    {
      label: 'Guest quiz sessions',
      value: data.guest_quiz_sessions,
      note: data.guest_quiz_sessions_note,
    },
    { label: 'Quiz attempts', value: data.quiz_attempts },
    { label: 'Questions answered', value: data.questions_answered },
    { label: 'Daily Practice sessions', value: data.daily_practice_sessions },
    {
      label: 'Average accuracy',
      value:
        data.average_accuracy == null ? null : `${data.average_accuracy}%`,
    },
    { label: 'Practice streak average', value: data.practice_streak_average },
    { label: 'Courses available', value: data.courses_available },
    { label: 'Total questions', value: data.total_questions },
    { label: 'Daily Active Users', value: data.daily_active_users },
    { label: 'Weekly Active Users', value: data.weekly_active_users },
    { label: 'Monthly Active Users', value: data.monthly_active_users },
  ]

  return (
    <div className="flex flex-col gap-6">
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
        {cards.map((card) => (
          <StatCard
            key={card.label}
            label={card.label}
            value={card.value}
            note={card.note}
          />
        ))}
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card>
          <h3 className="text-sm font-semibold text-gray-900">Newest registrations</h3>
          {data.recent_registrations?.length ? (
            <ul className="mt-3 divide-y divide-gray-100">
              {data.recent_registrations.map((u) => (
                <li
                  key={u.id}
                  className="flex flex-col gap-1 py-2 text-sm sm:flex-row sm:justify-between sm:gap-2"
                >
                  <span className="min-w-0 break-words text-gray-900">
                    {u.name}{' '}
                    <span className="text-gray-500">({u.email_masked || '—'})</span>
                  </span>
                  <span className="shrink-0 text-xs text-gray-400">
                    {formatDate(u.created_at)}
                  </span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="mt-3 text-sm text-gray-500">No registrations yet.</p>
          )}
        </Card>

        <Card>
          <h3 className="text-sm font-semibold text-gray-900">Newest quiz attempts</h3>
          {data.recent_quiz_attempts?.length ? (
            <ul className="mt-3 divide-y divide-gray-100">
              {data.recent_quiz_attempts.map((a) => (
                <li key={a.id} className="py-2 text-sm">
                  <div className="flex flex-col gap-1 sm:flex-row sm:justify-between sm:gap-2">
                    <span className="min-w-0 break-words text-gray-900">
                      #{a.id} · {a.course_name || 'Course'} · {a.mode}
                    </span>
                    <span className="shrink-0 text-xs text-gray-400">
                      {formatDate(a.started_at)}
                    </span>
                  </div>
                  <p className="text-xs text-gray-500">
                    User {a.user_id} · {a.questions_correct ?? '—'}/
                    {a.questions_total}
                    {a.completed_at ? ' · completed' : ' · in progress'}
                  </p>
                </li>
              ))}
            </ul>
          ) : (
            <p className="mt-3 text-sm text-gray-500">No attempts yet.</p>
          )}
        </Card>

        <Card>
          <h3 className="text-sm font-semibold text-gray-900">Newest feedback</h3>
          {data.recent_feedback?.length ? (
            <ul className="mt-3 divide-y divide-gray-100">
              {data.recent_feedback.map((f) => (
                <li key={f.id} className="py-2 text-sm">
                  <div className="flex items-center gap-2">
                    <Badge tone={f.rating === 'positive' ? 'green' : 'amber'}>
                      {f.rating === 'positive' ? '👍' : '👎'} {f.rating}
                    </Badge>
                    <span className="text-xs text-gray-400">
                      {formatDate(f.created_at)}
                    </span>
                  </div>
                  <p className="mt-1 text-gray-700">
                    {f.message || <span className="text-gray-400">No message</span>}
                  </p>
                </li>
              ))}
            </ul>
          ) : (
            <p className="mt-3 text-sm text-gray-500">No feedback yet.</p>
          )}
        </Card>

        <Card>
          <h3 className="text-sm font-semibold text-gray-900">Newest reports</h3>
          {data.recent_reports?.length ? (
            <ul className="mt-3 divide-y divide-gray-100">
              {data.recent_reports.map((r) => (
                <li
                  key={r.id}
                  className="flex flex-col gap-1 py-2 text-sm sm:flex-row sm:justify-between sm:gap-2"
                >
                  <span className="min-w-0 break-words">
                    Q{r.question_id} · {r.reason}{' '}
                    <Badge tone={statusTone(r.status)}>{r.status}</Badge>
                  </span>
                  <span className="shrink-0 text-xs text-gray-400">
                    {formatDate(r.created_at)}
                  </span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="mt-3 text-sm text-gray-500">No reports yet.</p>
          )}
        </Card>
      </div>
    </div>
  )
}

function ReportsSection({
  data,
  quality,
  loading,
  filters,
  onFiltersChange,
  onRefresh,
  onOpenQuestion,
}) {
  const [busyId, setBusyId] = useState(null)
  const [noteDrafts, setNoteDrafts] = useState({})

  const setNote = (id, value) => {
    setNoteDrafts((prev) => ({ ...prev, [id]: value }))
  }

  const updateStatus = async (id, status, existingNote) => {
    setBusyId(id)
    try {
      const raw =
        noteDrafts[id] !== undefined ? noteDrafts[id] : existingNote || ''
      const admin_note = String(raw).trim() || null
      await api(`/admin/reports/${id}`, {
        method: 'PATCH',
        body: { status, admin_note },
      })
      onRefresh()
    } finally {
      setBusyId(null)
    }
  }

  return (
    <div className="flex flex-col gap-4">
      {quality && (
        <Card className="!p-4">
          <h3 className="text-sm font-semibold text-gray-900">
            Question quality monitoring
          </h3>
          <div className="mt-3 grid grid-cols-2 gap-3 sm:grid-cols-3">
            <StatCard
              label="Unanswered reports"
              value={quality.unanswered_reports_count}
            />
            <StatCard
              label="Questions with multiple reports"
              value={quality.questions_with_multiple_reports}
            />
            <StatCard
              label="Top reported queue"
              value={quality.most_reported_questions?.length ?? 0}
              note="Shown below"
            />
          </div>
          {quality.most_reported_questions?.length > 0 && (
            <ul className="mt-4 divide-y divide-gray-100">
              {quality.most_reported_questions.map((q) => (
                <li
                  key={q.question_id}
                  className="flex flex-col gap-1 py-2 text-sm sm:flex-row sm:items-center sm:justify-between"
                >
                  <div className="min-w-0">
                    <button
                      type="button"
                      className={`font-medium text-blue-700 hover:underline ${FOCUS_RING}`}
                      onClick={() => onOpenQuestion(q.question_id)}
                    >
                      Q{q.question_id}
                      {q.course_code ? ` · ${q.course_code}` : ''}
                    </button>
                    <p className="truncate text-gray-600">{q.question_preview}</p>
                  </div>
                  <span className="shrink-0 text-xs text-gray-500">
                    {q.report_count} reports · {q.pending_count} pending
                  </span>
                </li>
              ))}
            </ul>
          )}
        </Card>
      )}

      <Card className="!p-4">
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4 lg:items-end">
          <div className="min-w-0 sm:col-span-2 lg:col-span-1">
            <label className="text-xs font-medium text-gray-700" htmlFor="report-search">
              Search
            </label>
            <input
              id="report-search"
              value={filters.search}
              onChange={(e) =>
                onFiltersChange({ ...filters, search: e.target.value })
              }
              placeholder="Question text, ID, course, reason…"
              autoComplete="off"
              className="mt-1 h-10 w-full rounded-md border border-gray-300 px-3 text-sm focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-600"
            />
          </div>
          <div className="min-w-0">
            <label className="text-xs font-medium text-gray-700" htmlFor="report-status">
              Status
            </label>
            <select
              id="report-status"
              value={filters.status}
              onChange={(e) =>
                onFiltersChange({ ...filters, status: e.target.value })
              }
              className="mt-1 h-10 w-full rounded-md border border-gray-300 px-3 text-sm focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-600"
            >
              <option value="all">All</option>
              <option value="pending">Pending</option>
              <option value="resolved">Resolved</option>
              <option value="ignored">Ignored</option>
            </select>
          </div>
          <div className="min-w-0">
            <label className="text-xs font-medium text-gray-700" htmlFor="report-reason">
              Reason
            </label>
            <select
              id="report-reason"
              value={filters.reason}
              onChange={(e) =>
                onFiltersChange({ ...filters, reason: e.target.value })
              }
              className="mt-1 h-10 w-full rounded-md border border-gray-300 px-3 text-sm focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-600"
            >
              {REPORT_REASON_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>
          <div className="min-w-0">
            <label className="text-xs font-medium text-gray-700" htmlFor="report-sort">
              Sort
            </label>
            <select
              id="report-sort"
              value={filters.sort}
              onChange={(e) =>
                onFiltersChange({ ...filters, sort: e.target.value })
              }
              className="mt-1 h-10 w-full rounded-md border border-gray-300 px-3 text-sm focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-600"
            >
              <option value="newest">Newest first</option>
              <option value="oldest">Oldest first</option>
            </select>
          </div>
        </div>
      </Card>

      {loading && <LoadingBlock />}

      {!loading && (!data?.items || data.items.length === 0) && (
        <EmptyState
          title="No question reports"
          description="Reports from students will appear here."
        />
      )}

      {!loading && data?.items?.length > 0 && (
        <>
          <ul className="flex flex-col gap-3 lg:hidden">
            {data.items.map((row) => (
              <li
                key={row.id}
                className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm"
              >
                <div className="flex flex-wrap items-start justify-between gap-2">
                  <div className="min-w-0">
                    <p className="text-sm font-semibold text-gray-900">
                      Q{row.question_id}
                      {row.course_code ? (
                        <span className="font-normal text-gray-500">
                          {' '}
                          · {row.course_code}
                        </span>
                      ) : null}
                    </p>
                    <p className="mt-1 text-xs text-gray-500">
                      {formatDate(row.reported_at)} · reported{' '}
                      {row.report_count_for_question}×
                      {row.has_reporter ? ' · signed-in reporter' : ' · anonymous'}
                    </p>
                  </div>
                  <Badge tone={statusTone(row.status)}>{row.status}</Badge>
                </div>
                <p className="mt-3 text-sm break-words text-gray-700">
                  {row.question_preview}
                </p>
                <p className="mt-2 text-xs font-medium text-gray-500">
                  Reason:{' '}
                  <span className="text-gray-800">{reasonLabel(row.reason)}</span>
                </p>
                {row.comment && (
                  <p className="mt-1 text-sm break-words text-gray-600">
                    {row.comment}
                  </p>
                )}
                {row.status_changed_at && (
                  <p className="mt-1 text-xs text-gray-500">
                    Status changed {formatDate(row.status_changed_at)}
                  </p>
                )}
                {row.admin_note && (
                  <p className="mt-1 text-xs text-gray-700">
                    Admin note: {row.admin_note}
                  </p>
                )}
                <label className="mt-3 block text-xs font-medium text-gray-700">
                  Admin note
                  <textarea
                    rows={2}
                    value={noteDrafts[row.id] ?? row.admin_note ?? ''}
                    onChange={(e) => setNote(row.id, e.target.value)}
                    className="mt-1 w-full rounded-md border border-gray-300 px-2 py-1 text-sm"
                    placeholder="Optional note when resolving or ignoring"
                  />
                </label>
                <div className="mt-4 flex flex-col gap-2">
                  <Button
                    className="w-full"
                    variant="secondary"
                    onClick={() => onOpenQuestion(row.question_id)}
                  >
                    Open question
                  </Button>
                  {row.status !== 'resolved' && (
                    <Button
                      className="w-full"
                      disabled={busyId === row.id}
                      onClick={() => updateStatus(row.id, 'resolved', row.admin_note)}
                    >
                      Resolve report
                    </Button>
                  )}
                  {row.status !== 'ignored' && (
                    <Button
                      className="w-full"
                      variant="ghost"
                      disabled={busyId === row.id}
                      onClick={() => updateStatus(row.id, 'ignored', row.admin_note)}
                    >
                      Ignore report
                    </Button>
                  )}
                  {row.status !== 'pending' && (
                    <Button
                      className="w-full"
                      variant="ghost"
                      disabled={busyId === row.id}
                      onClick={() => updateStatus(row.id, 'pending', row.admin_note)}
                    >
                      Reopen
                    </Button>
                  )}
                </div>
              </li>
            ))}
          </ul>

          <div className="hidden overflow-x-auto rounded-lg border border-gray-200 bg-white shadow-sm lg:block">
            <table className="min-w-full divide-y divide-gray-200 text-left text-sm">
              <caption className="sr-only">
                Question reports with course, reason, status, and actions
              </caption>
              <thead className="bg-gray-50 text-xs font-medium uppercase text-gray-600">
                <tr>
                  <th scope="col" className="px-3 py-2">Course</th>
                  <th scope="col" className="px-3 py-2">Q ID</th>
                  <th scope="col" className="px-3 py-2">Preview</th>
                  <th scope="col" className="px-3 py-2">Reason</th>
                  <th scope="col" className="px-3 py-2">Comment</th>
                  <th scope="col" className="px-3 py-2">Date</th>
                  <th scope="col" className="px-3 py-2">Status</th>
                  <th scope="col" className="px-3 py-2">Times</th>
                  <th scope="col" className="px-3 py-2">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {data.items.map((row) => (
                  <tr key={row.id} className="align-top">
                    <td className="px-3 py-2 whitespace-nowrap">
                      {row.course_code || '—'}
                    </td>
                    <td className="px-3 py-2 font-medium text-gray-900">
                      {row.question_id}
                    </td>
                    <td className="max-w-xs px-3 py-2 break-words text-gray-700">
                      {row.question_preview}
                    </td>
                    <td className="px-3 py-2 whitespace-nowrap">
                      {reasonLabel(row.reason)}
                    </td>
                    <td className="max-w-xs px-3 py-2 break-words text-gray-600">
                      {row.comment || '—'}
                      {row.admin_note ? (
                        <p className="mt-1 text-xs text-gray-500">
                          Note: {row.admin_note}
                        </p>
                      ) : null}
                      {row.status_changed_at ? (
                        <p className="mt-1 text-xs text-gray-400">
                          Changed {formatDate(row.status_changed_at)}
                        </p>
                      ) : null}
                    </td>
                    <td className="px-3 py-2 whitespace-nowrap text-xs text-gray-500">
                      {formatDate(row.reported_at)}
                    </td>
                    <td className="px-3 py-2">
                      <Badge tone={statusTone(row.status)}>{row.status}</Badge>
                    </td>
                    <td className="px-3 py-2 text-center">
                      {row.report_count_for_question}
                    </td>
                    <td className="px-3 py-2">
                      <textarea
                        rows={2}
                        value={noteDrafts[row.id] ?? row.admin_note ?? ''}
                        onChange={(e) => setNote(row.id, e.target.value)}
                        className="mb-2 w-40 rounded-md border border-gray-300 px-2 py-1 text-xs"
                        placeholder="Admin note"
                      />
                      <div className="flex flex-col gap-1">
                        <Button
                          variant="secondary"
                          onClick={() => onOpenQuestion(row.question_id)}
                        >
                          Open question
                        </Button>
                        {row.status !== 'resolved' && (
                          <Button
                            disabled={busyId === row.id}
                            onClick={() => updateStatus(row.id, 'resolved', row.admin_note)}
                          >
                            Resolve report
                          </Button>
                        )}
                        {row.status !== 'ignored' && (
                          <Button
                            variant="ghost"
                            disabled={busyId === row.id}
                            onClick={() => updateStatus(row.id, 'ignored', row.admin_note)}
                          >
                            Ignore report
                          </Button>
                        )}
                        {row.status !== 'pending' && (
                          <Button
                            variant="ghost"
                            disabled={busyId === row.id}
                            onClick={() => updateStatus(row.id, 'pending', row.admin_note)}
                          >
                            Reopen
                          </Button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <p className="text-xs text-gray-500">
            Showing {data.items.length} of {data.total} reports
          </p>
        </>
      )}
    </div>
  )
}

function FeedbackSection({ data, filters, onFiltersChange, onRefresh }) {
  const [busyId, setBusyId] = useState(null)

  if (!data) return <LoadingBlock />

  const markReviewed = async (id) => {
    setBusyId(id)
    try {
      await api(`/admin/feedback/${id}/review`, { method: 'POST' })
      onRefresh()
    } finally {
      setBusyId(null)
    }
  }

  return (
    <div className="flex flex-col gap-4">
      <Card className="!p-4">
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <div>
            <label className="text-xs font-medium text-gray-700" htmlFor="fb-sentiment">
              Sentiment
            </label>
            <select
              id="fb-sentiment"
              value={filters.rating}
              onChange={(e) =>
                onFiltersChange({ ...filters, rating: e.target.value })
              }
              className="mt-1 h-10 w-full rounded-md border border-gray-300 px-3 text-sm"
            >
              <option value="all">All</option>
              <option value="positive">Positive</option>
              <option value="negative">Negative</option>
            </select>
          </div>
          <div>
            <label className="text-xs font-medium text-gray-700" htmlFor="fb-since">
              From date
            </label>
            <input
              id="fb-since"
              type="date"
              value={filters.since}
              onChange={(e) =>
                onFiltersChange({ ...filters, since: e.target.value })
              }
              className="mt-1 h-10 w-full rounded-md border border-gray-300 px-3 text-sm"
            />
          </div>
          <div>
            <label className="text-xs font-medium text-gray-700" htmlFor="fb-until">
              To date
            </label>
            <input
              id="fb-until"
              type="date"
              value={filters.until}
              onChange={(e) =>
                onFiltersChange({ ...filters, until: e.target.value })
              }
              className="mt-1 h-10 w-full rounded-md border border-gray-300 px-3 text-sm"
            />
          </div>
          <div className="flex items-end">
            <label className="flex min-h-10 items-center gap-2 text-sm text-gray-800">
              <input
                type="checkbox"
                checked={filters.unreadOnly}
                onChange={(e) =>
                  onFiltersChange({ ...filters, unreadOnly: e.target.checked })
                }
              />
              Unread only
            </label>
          </div>
        </div>
      </Card>

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <StatCard label="Total (filtered)" value={data.total} />
        <StatCard
          label="Unread / new"
          value={data.unread_count}
          note="Admin has not reviewed yet"
        />
        <StatCard
          label="Positive %"
          value={data.positive_percent == null ? null : `${data.positive_percent}%`}
          note={`${data.positive_count} positive`}
        />
        <StatCard
          label="Negative %"
          value={data.negative_percent == null ? null : `${data.negative_percent}%`}
          note={`${data.negative_count} negative`}
        />
      </div>

      {data.by_sentiment && (
        <Card>
          <h3 className="text-sm font-semibold text-gray-900">
            Sentiment grouping (all stored feedback)
          </h3>
          <div className="mt-3 grid grid-cols-3 gap-3">
            <StatCard label="Positive" value={data.by_sentiment.positive} />
            <StatCard label="Negative" value={data.by_sentiment.negative} />
            <StatCard label="Other / unrated" value={data.by_sentiment.other} />
          </div>
        </Card>
      )}

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card>
          <h3 className="text-sm font-semibold text-gray-900">Most common words</h3>
          {data.most_common_words?.length ? (
            <ul className="mt-3 flex flex-wrap gap-2">
              {data.most_common_words.map((w) => (
                <li key={w.word}>
                  <Badge tone="blue">
                    {w.word} · {w.count}
                  </Badge>
                </li>
              ))}
            </ul>
          ) : (
            <p className="mt-3 text-sm text-gray-500">No written feedback yet.</p>
          )}
        </Card>

        <Card>
          <h3 className="text-sm font-semibold text-gray-900">Newest feedback</h3>
          {data.newest?.length ? (
            <ul className="mt-3 divide-y divide-gray-100">
              {data.newest.map((f) => (
                <li key={f.id} className="py-2 text-sm">
                  <div className="flex flex-wrap items-center gap-2">
                    <span>{f.rating === 'positive' ? '👍' : '👎'}</span>
                    {f.is_unread && <Badge tone="blue">New</Badge>}
                    <Badge tone={f.is_anonymous ? 'gray' : 'blue'}>
                      {f.is_anonymous ? 'Anonymous' : 'Logged-in'}
                    </Badge>
                    <span className="text-xs text-gray-500">
                      {f.course_code || 'Course'} · {formatDate(f.created_at)}
                    </span>
                  </div>
                  <p className="mt-1 text-gray-700">
                    {f.message || <span className="text-gray-400">No message</span>}
                  </p>
                </li>
              ))}
            </ul>
          ) : (
            <p className="mt-3 text-sm text-gray-500">No feedback yet.</p>
          )}
        </Card>
      </div>

      <Card>
        <h3 className="text-sm font-semibold text-gray-900">Feedback list</h3>
        {!data.items?.length ? (
          <EmptyState
            title="No feedback"
            description="Student thumbs-up / thumbs-down responses will appear here."
          />
        ) : (
          <ul className="mt-3 divide-y divide-gray-100">
            {data.items.map((f) => (
              <li
                key={f.id}
                className="flex flex-col gap-2 py-3 text-sm sm:flex-row sm:items-start sm:justify-between"
              >
                <div>
                  <div className="flex flex-wrap items-center gap-2">
                    <span>
                      {f.rating === 'positive' ? '👍 positive' : '👎 negative'}
                    </span>
                    {f.is_unread && <Badge tone="blue">New</Badge>}
                  </div>
                  <p className="mt-1 text-gray-700">
                    {f.message || <span className="text-gray-400">—</span>}
                  </p>
                  <p className="mt-1 text-xs text-gray-500">
                    {f.course_name || f.course_code || '—'} ·{' '}
                    {f.is_anonymous ? 'Anonymous' : 'Logged-in'} ·{' '}
                    {formatDate(f.created_at)}
                  </p>
                </div>
                {f.is_unread && (
                  <Button
                    variant="secondary"
                    disabled={busyId === f.id}
                    onClick={() => markReviewed(f.id)}
                  >
                    Mark reviewed
                  </Button>
                )}
              </li>
            ))}
          </ul>
        )}
      </Card>
    </div>
  )
}

function AnalyticsSection({ data }) {
  if (!data) return <LoadingBlock />

  const courseBars = (data.most_attempted_courses || []).map((c) => ({
    label: c.course_code,
    value: c.attempts,
  }))
  const hardBars = (data.most_difficult_topics || []).map((t) => ({
    label: `${t.course_code}: ${t.topic_name}`,
    value: t.accuracy,
    suffix: '%',
  }))
  const highBars = (data.highest_accuracy_topics || []).map((t) => ({
    label: `${t.course_code}: ${t.topic_name}`,
    value: t.accuracy,
    suffix: '%',
  }))

  return (
    <div className="flex flex-col gap-4">
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
        <StatCard
          label="Average quiz score"
          value={
            data.average_quiz_score == null ? null : `${data.average_quiz_score}%`
          }
        />
        <StatCard
          label="Avg quiz duration"
          value={
            data.average_quiz_duration_seconds == null
              ? null
              : `${Math.round(data.average_quiz_duration_seconds / 60)} min`
          }
        />
        <StatCard
          label="Avg questions / session"
          value={data.average_questions_per_session}
        />
        <StatCard
          label="Daily Practice completion"
          value={
            data.daily_practice_completion_percent == null
              ? null
              : `${data.daily_practice_completion_percent}%`
          }
        />
        <StatCard
          label="Weakness Map users"
          value={data.weakness_map_users}
          note={data.weakness_map_note}
        />
        <StatCard
          label="Registered attempts"
          value={data.guest_vs_registered?.registered_quiz_attempts}
        />
        <StatCard
          label="Guest feedback (proxy)"
          value={data.guest_vs_registered?.guest_feedback_submissions}
          note="Guest sessions are not persisted"
        />
        <StatCard
          label="Top searched topics"
          value={null}
          note={data.top_searched_topics_note}
        />
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <Card>
          <h3 className="mb-3 text-sm font-semibold text-gray-900">
            Most attempted courses
          </h3>
          <BarList items={courseBars} />
        </Card>
        <Card>
          <h3 className="mb-3 text-sm font-semibold text-gray-900">
            Most difficult topics
          </h3>
          <BarList items={hardBars} />
        </Card>
        <Card>
          <h3 className="mb-3 text-sm font-semibold text-gray-900">
            Highest accuracy topics
          </h3>
          <BarList items={highBars} />
        </Card>
      </div>
    </div>
  )
}

function HealthSection({ data }) {
  if (!data) return <LoadingBlock />
  const maxQ = Math.max(
    1,
    ...(data.questions_by_course || []).map((c) => c.question_count),
  )

  return (
    <div className="flex flex-col gap-4">
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
        <StatCard label="Total users" value={data.total_users} />
        <StatCard label="Total attempts" value={data.total_attempts} />
        <StatCard label="Total answers" value={data.total_answers} />
        <StatCard label="Total questions" value={data.total_questions} />
        <StatCard label="Reports waiting" value={data.reports_waiting} />
        <StatCard
          label="Database size"
          value={data.database_size_label}
          note={
            data.database_size_bytes != null
              ? `${data.database_size_bytes.toLocaleString()} bytes`
              : undefined
          }
        />
        <StatCard
          label="Last backup"
          value={data.last_backup}
          note={data.last_backup_note}
        />
        <StatCard
          label="Health check"
          value={data.health_status}
          note={`Database: ${data.database_status}`}
        />
        <StatCard
          label="Integrity"
          value={
            data.integrity
              ? data.integrity.ok
                ? 'OK'
                : `${data.integrity.issue_count} issue(s)`
              : '—'
          }
          note={
            data.integrity?.ok
              ? 'No orphaned rows or broken relationships detected.'
              : data.integrity
                ? 'See integrity details below.'
                : undefined
          }
        />
      </div>

      {data.integrity && !data.integrity.ok && (
        <Card>
          <h3 className="text-sm font-semibold text-gray-900">
            Data integrity issues
          </h3>
          <ul className="mt-3 divide-y divide-gray-100">
            {(data.integrity.checks || [])
              .filter((c) => !c.ok)
              .map((c) => (
                <li key={c.key} className="py-2 text-sm text-gray-800">
                  <span className="font-medium">{c.label}</span>
                  {c.detail ? (
                    <span className="text-gray-600"> — {c.detail}</span>
                  ) : null}
                </li>
              ))}
          </ul>
        </Card>
      )}

      <Card>
        <h3 className="text-sm font-semibold text-gray-900">Questions by course</h3>
        <ul className="mt-4 flex flex-col gap-3">
          {(data.questions_by_course || []).map((c) => (
            <li key={c.course_code}>
              <div className="mb-1 flex items-start justify-between gap-2 text-sm">
                <span className="min-w-0 break-words font-medium text-gray-900">
                  {c.course_code} — {c.course_name}
                </span>
                <span className="shrink-0 text-gray-600">{c.question_count}</span>
              </div>
              <ProgressBar
                value={c.question_count}
                max={maxQ}
                label={`Questions in ${c.course_code}`}
              />
            </li>
          ))}
        </ul>
      </Card>
    </div>
  )
}

function ImpactSection({ data }) {
  if (!data) return <LoadingBlock />

  return (
    <div className="flex flex-col gap-4">
      <p className="text-sm text-gray-600">
        Real metrics only — values are computed from production database rows. Empty
        or unavailable metrics show as —.
      </p>
      <h3 className="text-sm font-semibold text-gray-900">Platform totals</h3>
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
        <StatCard label="Registered users" value={data.registered_users} />
        <StatCard label="Quiz attempts" value={data.quiz_attempts} />
        <StatCard label="Questions answered" value={data.questions_answered} />
        <StatCard label="Courses practiced" value={data.courses_practiced} />
        <StatCard label="Feedback submitted" value={data.feedback_submitted} />
        <StatCard label="Reports submitted" value={data.reports_submitted} />
        <StatCard label="Students helped" value={data.students_helped} />
        <StatCard
          label="Practice sessions completed"
          value={data.practice_sessions_completed}
        />
      </div>

      <h3 className="text-sm font-semibold text-gray-900">Growth (last 7 days)</h3>
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
        <StatCard label="New users (7d)" value={data.users_last_7_days} />
        <StatCard label="Quizzes started (7d)" value={data.quizzes_last_7_days} />
      </div>

      <h3 className="text-sm font-semibold text-gray-900">Learning outcomes</h3>
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
        <StatCard
          label="Daily practices completed"
          value={data.daily_practices_completed}
        />
        <StatCard
          label="Average improvement"
          value={
            data.average_improvement == null
              ? null
              : `${data.average_improvement > 0 ? '+' : ''}${data.average_improvement} pts`
          }
          note={data.average_improvement_note}
        />
        <StatCard label="Strong topics mastered" value={data.strong_topics_mastered} />
        <StatCard label="Weaknesses identified" value={data.weaknesses_identified} />
        <StatCard label="Questions reported" value={data.questions_reported} />
        <StatCard
          label="Questions reported and fixed"
          value={data.questions_fixed}
          note="Distinct questions marked resolved"
        />
        <StatCard label="Feedback received" value={data.feedback_received} />
      </div>
    </div>
  )
}

function QuestionModal({ questionId, onClose }) {
  const [detail, setDetail] = useState(null)
  const [error, setError] = useState(null)
  const titleId = useId()
  const handleEscape = useCallback(() => {
    onClose?.()
  }, [onClose])
  const dialogRef = useFocusTrap(Boolean(questionId), handleEscape)

  useEffect(() => {
    if (!questionId) return
    setDetail(null)
    setError(null)
    api(`/admin/questions/${questionId}`)
      .then(setDetail)
      .catch((err) => setError(err.message))
  }, [questionId])

  useEffect(() => {
    if (!questionId) return undefined
    const previousOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    return () => {
      document.body.style.overflow = previousOverflow
    }
  }, [questionId])

  if (!questionId) return null

  return (
    <div
      className="fixed inset-0 z-50 flex items-end justify-center bg-gray-900/50 p-3 sm:items-center sm:p-4"
      onClick={(event) => {
        if (event.target === event.currentTarget) onClose?.()
      }}
    >
      <div
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        className="max-h-[90vh] w-full max-w-2xl overflow-x-clip overflow-y-auto rounded-lg border border-gray-200 bg-white p-4 shadow-lg sm:p-6"
      >
        <div className="flex items-start justify-between gap-3">
          <h3 id={titleId} className="min-w-0 text-lg font-semibold break-words text-gray-900">
            Question #{questionId}
          </h3>
          <Button className="shrink-0" variant="ghost" onClick={onClose} aria-label="Close question details">
            Close
          </Button>
        </div>
        {error && (
          <p role="alert" className="mt-4 text-sm text-red-700">
            {error}
          </p>
        )}
        {!detail && !error && (
          <p className="mt-4 text-sm text-gray-600" role="status">
            Loading…
          </p>
        )}
        {detail && (
          <div className="mt-4 flex flex-col gap-3 text-sm">
            <p className="text-xs text-gray-600">
              {detail.course_code} · {detail.topic_name} · {detail.question_type}
              {detail.difficulty ? ` · ${detail.difficulty}` : ''}
            </p>
            <p className="whitespace-pre-wrap break-words text-gray-900">
              {detail.question_text}
            </p>
            {detail.choices?.length > 0 && (
              <ul className="flex flex-col gap-1" aria-label="Answer choices">
                {detail.choices.map((c) => (
                  <li
                    key={c.id}
                    className={
                      c.is_correct
                        ? 'rounded-md bg-green-50 px-3 py-2 text-green-900'
                        : 'rounded-md bg-gray-50 px-3 py-2 text-gray-800'
                    }
                  >
                    {c.choice_text}
                    {c.is_correct ? (
                      <span className="sr-only"> (correct)</span>
                    ) : null}
                    {c.is_correct ? (
                      <span aria-hidden="true"> ✓</span>
                    ) : null}
                  </li>
                ))}
              </ul>
            )}
            {detail.answer && (
              <p>
                <span className="font-medium">Answer: </span>
                {detail.answer}
              </p>
            )}
            {detail.explanation && (
              <p className="text-gray-800">
                <span className="font-medium">Explanation: </span>
                {detail.explanation}
              </p>
            )}
            <p className="text-xs text-gray-600">
              Reported {detail.report_count} time{detail.report_count === 1 ? '' : 's'}
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

function ReliabilitySection({ data }) {
  if (!data) return <LoadingBlock />

  const cards = [
    { label: 'Total users', value: data.total_users },
    { label: 'Total quizzes', value: data.total_quizzes },
    { label: 'Feedback count', value: data.feedback_count },
    { label: 'Reported questions', value: data.reported_questions },
    { label: 'Pending reports', value: data.pending_reports },
    {
      label: 'Error tracking',
      value: data.sentry_configured ? 'Configured' : 'Not configured',
      note: data.sentry_configured
        ? 'Sentry enabled for this production environment.'
        : 'Set SENTRY_DSN in production to enable remote error tracking.',
    },
    { label: 'API version', value: data.version },
    {
      label: 'Uptime',
      value: `${Math.floor((data.uptime_seconds || 0) / 60)} min`,
    },
  ]

  return (
    <div className="flex flex-col gap-6">
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
        {cards.map((card) => (
          <StatCard
            key={card.label}
            label={card.label}
            value={card.value}
            note={card.note}
          />
        ))}
      </div>

      <Card>
        <h3 className="text-sm font-semibold text-gray-900">Recent API errors</h3>
        <p className="mt-1 text-xs text-gray-500">
          Sanitized process-local errors (no passwords, tokens, or answers). Cleared on
          restart.
        </p>
        {data.recent_errors?.length ? (
          <ul className="mt-3 divide-y divide-gray-100">
            {data.recent_errors.map((err, index) => (
              <li key={`${err.ts}-${index}`} className="py-2 text-sm">
                <div className="flex flex-col gap-1 sm:flex-row sm:justify-between">
                  <span className="min-w-0 break-words text-gray-900">
                    {err.status_code} · {err.error_type} · {err.endpoint}
                  </span>
                  <span className="shrink-0 text-xs text-gray-400">
                    {formatDate(err.ts * 1000)}
                  </span>
                </div>
                <p className="mt-0.5 text-xs text-gray-600">{err.message}</p>
              </li>
            ))}
          </ul>
        ) : (
          <p className="mt-3 text-sm text-gray-500">No recent errors recorded.</p>
        )}
      </Card>
    </div>
  )
}

function Admin() {
  const [section, setSection] = useState('overview')
  const [overview, setOverview] = useState(null)
  const [reliability, setReliability] = useState(null)
  const [reports, setReports] = useState(null)
  const [questionQuality, setQuestionQuality] = useState(null)
  const [feedback, setFeedback] = useState(null)
  const [analytics, setAnalytics] = useState(null)
  const [health, setHealth] = useState(null)
  const [impact, setImpact] = useState(null)
  const [error, setError] = useState(null)
  const [reportsLoading, setReportsLoading] = useState(false)
  const [reportFilters, setReportFilters] = useState({
    status: 'all',
    reason: 'all',
    search: '',
    sort: 'newest',
  })
  const [feedbackFilters, setFeedbackFilters] = useState({
    rating: 'all',
    since: '',
    until: '',
    unreadOnly: false,
  })
  const [openQuestionId, setOpenQuestionId] = useState(null)

  const searchDebounced = useMemo(() => reportFilters.search, [reportFilters.search])

  const loadOverview = useCallback(() => {
    return api('/admin/overview').then(setOverview)
  }, [])

  const loadReliability = useCallback(() => {
    return api('/admin/reliability').then(setReliability)
  }, [])

  const loadReports = useCallback(() => {
    setReportsLoading(true)
    const params = new URLSearchParams({
      status: reportFilters.status,
      reason: reportFilters.reason,
      sort: reportFilters.sort,
    })
    if (searchDebounced.trim()) params.set('search', searchDebounced.trim())
    return Promise.all([
      api(`/admin/reports?${params}`),
      api('/admin/question-quality'),
    ])
      .then(([reportData, qualityData]) => {
        setReports(reportData)
        setQuestionQuality(qualityData)
      })
      .finally(() => setReportsLoading(false))
  }, [
    reportFilters.status,
    reportFilters.reason,
    reportFilters.sort,
    searchDebounced,
  ])

  const loadFeedback = useCallback(() => {
    const params = new URLSearchParams()
    if (feedbackFilters.rating !== 'all') {
      params.set('rating', feedbackFilters.rating)
    }
    if (feedbackFilters.unreadOnly) params.set('unread_only', 'true')
    if (feedbackFilters.since) {
      params.set('since', `${feedbackFilters.since}T00:00:00`)
    }
    if (feedbackFilters.until) {
      params.set('until', `${feedbackFilters.until}T23:59:59`)
    }
    const qs = params.toString()
    return api(`/admin/feedback${qs ? `?${qs}` : ''}`).then(setFeedback)
  }, [feedbackFilters])

  useEffect(() => {
    setError(null)
    const loaders = {
      overview: () => loadOverview(),
      reliability: () => loadReliability(),
      reports: () => loadReports(),
      feedback: () => loadFeedback(),
      analytics: () => api('/admin/analytics').then(setAnalytics),
      health: () =>
        Promise.all([api('/admin/health'), api('/admin/integrity')]).then(
          ([healthData, integrityData]) =>
            setHealth({ ...healthData, integrity: integrityData }),
        ),
      impact: () => api('/admin/impact').then(setImpact),
    }
    const loader = loaders[section]
    if (!loader) return
    loader().catch((err) => setError(err.message))
  }, [section, loadOverview, loadReliability, loadReports, loadFeedback])

  // Debounce report search slightly by re-triggering when filters change
  useEffect(() => {
    if (section !== 'reports') return
    const t = setTimeout(() => {
      loadReports().catch((err) => setError(err.message))
    }, 250)
    return () => clearTimeout(t)
  }, [reportFilters.search, section, loadReports])

  useEffect(() => {
    if (section !== 'feedback') return
    loadFeedback().catch((err) => setError(err.message))
  }, [feedbackFilters, section, loadFeedback])

  return (
    <AppLayout pageTitle="Admin" documentTitle="Admin | ABDiploma Hub">
      <div className="mx-auto flex max-w-6xl flex-col gap-6">
        <div>
          <h2 className="text-xl font-bold text-gray-900">Admin Dashboard</h2>
          <p className="mt-1 text-sm text-gray-600">
            Production metrics, reports, and feedback for ABDiploma Hub operators.
          </p>
        </div>

        <SectionNav active={section} onChange={setSection} />

        {error && (
          <div
            role="alert"
            className="rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800"
          >
            {error}
          </div>
        )}

        <div
          role="tabpanel"
          id={`admin-panel-${section}`}
          aria-labelledby={`admin-tab-${section}`}
        >
          {section === 'overview' && <OverviewSection data={overview} />}
          {section === 'reliability' && <ReliabilitySection data={reliability} />}
          {section === 'reports' && (
            <ReportsSection
              data={reports}
              quality={questionQuality}
              loading={reportsLoading}
              filters={reportFilters}
              onFiltersChange={setReportFilters}
              onRefresh={loadReports}
              onOpenQuestion={setOpenQuestionId}
            />
          )}
          {section === 'feedback' && (
            <FeedbackSection
              data={feedback}
              filters={feedbackFilters}
              onFiltersChange={setFeedbackFilters}
              onRefresh={loadFeedback}
            />
          )}
          {section === 'analytics' && <AnalyticsSection data={analytics} />}
          {section === 'health' && <HealthSection data={health} />}
          {section === 'impact' && <ImpactSection data={impact} />}
        </div>
      </div>

      <QuestionModal
        questionId={openQuestionId}
        onClose={() => setOpenQuestionId(null)}
      />
    </AppLayout>
  )
}

export default Admin
