export interface Interview {
  id: number;
  candidate_id: number;
  interviewer: string;
  interview_date: string;
  interview_time: string;
  interview_mode: string;
  meeting_link?: string;
  status: string;
  created_at?: string;
}

export interface Candidate {
  id: number;
  name: string;
  email: string;
}

export interface InterviewFormData {
  candidate_id: number | "";
  interviewer: string;
  interview_date: string;
  interview_time: string;
  interview_mode: string;
  meeting_link: string;
}