import React from "react";
import type { InterviewFormData, Candidate } from "./types";

interface Props {
  formData: InterviewFormData;
  setFormData: React.Dispatch<React.SetStateAction<InterviewFormData>>;
  candidates: Candidate[];
  onSubmit: (e: React.FormEvent) => void;
  isEditing: boolean;
}

const InterviewForm: React.FC<Props> = ({
  formData,
  setFormData,
  candidates,
  onSubmit,
  isEditing,
}) => {
  return (
    <div className="bg-gray-900 border border-gray-700 rounded-xl p-6 mb-8">
      <h2 className="text-xl font-bold text-white mb-6">
        {isEditing ? "Update Interview" : "Schedule Interview"}
      </h2>

      <form
        onSubmit={onSubmit}
        className="grid grid-cols-1 md:grid-cols-2 gap-5"
      >
        {/* Candidate */}

        <div>
          <label className="block text-sm text-gray-300 mb-2">
            Candidate
          </label>

          <select
            value={formData.candidate_id}
            onChange={(e) =>
              setFormData({
                ...formData,
                candidate_id: Number(e.target.value),
              })
            }
            className="w-full rounded-lg bg-gray-800 border border-gray-600 px-4 py-2 text-white"
            required
          >
            <option value="">Select Candidate</option>

            {candidates.map((candidate) => (
              <option
                key={candidate.id}
                value={candidate.id}
              >
                {candidate.name}
              </option>
            ))}
          </select>
        </div>

        {/* Interviewer */}

        <div>
          <label className="block text-sm text-gray-300 mb-2">
            Interviewer
          </label>

          <input
            type="text"
            value={formData.interviewer}
            onChange={(e) =>
              setFormData({
                ...formData,
                interviewer: e.target.value,
              })
            }
            className="w-full rounded-lg bg-gray-800 border border-gray-600 px-4 py-2 text-white"
            placeholder="John Smith"
            required
          />
        </div>

        {/* Date */}

        <div>
          <label className="block text-sm text-gray-300 mb-2">
            Interview Date
          </label>

          <input
            type="date"
            value={formData.interview_date}
            onChange={(e) =>
              setFormData({
                ...formData,
                interview_date: e.target.value,
              })
            }
            className="w-full rounded-lg bg-gray-800 border border-gray-600 px-4 py-2 text-white"
            required
          />
        </div>

        {/* Time */}

        <div>
          <label className="block text-sm text-gray-300 mb-2">
            Interview Time
          </label>

          <input
            type="time"
            value={formData.interview_time}
            onChange={(e) =>
              setFormData({
                ...formData,
                interview_time: e.target.value,
              })
            }
            className="w-full rounded-lg bg-gray-800 border border-gray-600 px-4 py-2 text-white"
            required
          />
        </div>

        {/* Mode */}

        <div>
          <label className="block text-sm text-gray-300 mb-2">
            Interview Mode
          </label>

          <select
            value={formData.interview_mode}
            onChange={(e) =>
              setFormData({
                ...formData,
                interview_mode: e.target.value,
              })
            }
            className="w-full rounded-lg bg-gray-800 border border-gray-600 px-4 py-2 text-white"
          >
            <option value="Online">Online</option>
            <option value="Offline">Offline</option>
          </select>
        </div>

        {/* Meeting Link */}

        <div>
          <label className="block text-sm text-gray-300 mb-2">
            Meeting Link
          </label>

          <input
            type="text"
            value={formData.meeting_link}
            onChange={(e) =>
              setFormData({
                ...formData,
                meeting_link: e.target.value,
              })
            }
            placeholder="https://meet.google.com/..."
            className="w-full rounded-lg bg-gray-800 border border-gray-600 px-4 py-2 text-white"
          />
        </div>

        <div className="md:col-span-2">
          <button
            type="submit"
            className="w-full bg-blue-600 hover:bg-blue-700 transition py-3 rounded-lg text-white font-semibold"
          >
            {isEditing
              ? "Update Interview"
              : "Schedule Interview"}
          </button>
        </div>
      </form>
    </div>
  );
};

export default InterviewForm;