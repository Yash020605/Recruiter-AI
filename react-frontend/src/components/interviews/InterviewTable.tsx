import React from "react";
import { Edit2, Trash2, ExternalLink } from "lucide-react";
import type { Interview } from "./types";

interface Props {
  interviews: Interview[];
  onEdit: (interview: Interview) => void;
  onDelete: (id: number) => void;
}

const statusColor = (status: string) => {
  switch (status.toLowerCase()) {
    case "scheduled":
      return "bg-blue-500/20 text-blue-300";

    case "completed":
      return "bg-green-500/20 text-green-300";

    case "cancelled":
      return "bg-red-500/20 text-red-300";

    default:
      return "bg-gray-500/20 text-gray-300";
  }
};

const InterviewTable: React.FC<Props> = ({
  interviews,
  onEdit,
  onDelete,
}) => {
  if (interviews.length === 0) {
    return (
      <div className="bg-gray-900 border border-gray-700 rounded-xl p-6 text-center text-gray-400">
        No interviews scheduled yet.
      </div>
    );
  }

  return (
    <div className="bg-gray-900 border border-gray-700 rounded-xl overflow-hidden">

      <div className="overflow-x-auto">

        <table className="min-w-full">

          <thead className="bg-gray-800">

            <tr>

              <th className="px-5 py-3 text-left text-sm font-semibold text-gray-300">
                Candidate ID
              </th>

              <th className="px-5 py-3 text-left text-sm font-semibold text-gray-300">
                Interviewer
              </th>

              <th className="px-5 py-3 text-left text-sm font-semibold text-gray-300">
                Date
              </th>

              <th className="px-5 py-3 text-left text-sm font-semibold text-gray-300">
                Time
              </th>

              <th className="px-5 py-3 text-left text-sm font-semibold text-gray-300">
                Mode
              </th>

              <th className="px-5 py-3 text-left text-sm font-semibold text-gray-300">
                Meeting
              </th>

              <th className="px-5 py-3 text-left text-sm font-semibold text-gray-300">
                Status
              </th>

              <th className="px-5 py-3 text-center text-sm font-semibold text-gray-300">
                Actions
              </th>

            </tr>

          </thead>

          <tbody>

            {interviews.map((interview) => (

              <tr
                key={interview.id}
                className="border-t border-gray-800 hover:bg-gray-800/40 transition"
              >

                <td className="px-5 py-4 text-white">
                  {interview.candidate_id}
                </td>

                <td className="px-5 py-4 text-gray-300">
                  {interview.interviewer}
                </td>

                <td className="px-5 py-4 text-gray-300">
                  {interview.interview_date}
                </td>

                <td className="px-5 py-4 text-gray-300">
                  {interview.interview_time}
                </td>

                <td className="px-5 py-4 text-gray-300">
                  {interview.interview_mode}
                </td>

                <td className="px-5 py-4">

                  {interview.meeting_link ? (

                    <a
                      href={interview.meeting_link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-400 hover:text-blue-300 flex items-center gap-1"
                    >
                      Open
                      <ExternalLink size={14} />
                    </a>

                  ) : (

                    <span className="text-gray-500">
                      —
                    </span>

                  )}

                </td>

                <td className="px-5 py-4">

                  <span
                    className={`px-3 py-1 rounded-full text-xs font-semibold ${statusColor(
                      interview.status
                    )}`}
                  >
                    {interview.status}
                  </span>

                </td>

                <td className="px-5 py-4">

                  <div className="flex justify-center gap-3">

                    <button
                      onClick={() => onEdit(interview)}
                      className="text-yellow-400 hover:text-yellow-300"
                    >
                      <Edit2 size={18} />
                    </button>

                    <button
                      onClick={() => onDelete(interview.id)}
                      className="text-red-400 hover:text-red-300"
                    >
                      <Trash2 size={18} />
                    </button>

                  </div>

                </td>

              </tr>

            ))}

          </tbody>

        </table>

      </div>

    </div>
  );
};

export default InterviewTable;