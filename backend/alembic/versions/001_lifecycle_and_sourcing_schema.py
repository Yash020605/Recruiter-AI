"""recruitment_lifecycle_and_sourcing_schema

Revision ID: 001_lifecycle_sourcing
Revises: 
Create Date: 2026-08-16 13:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '001_lifecycle_sourcing'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Jobs
    op.create_table(
        'jobs',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('department', sa.String(), nullable=True),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('requirements', sa.Text(), nullable=True),
        sa.Column('status', sa.String(), nullable=False, server_default='Active'),
        sa.Column('created_by_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'))
    )
    op.create_index('ix_jobs_id', 'jobs', ['id'])
    op.create_index('ix_jobs_title', 'jobs', ['title'])

    # Recruitment Stages
    op.create_table(
        'recruitment_stages',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('job_id', sa.Integer(), sa.ForeignKey('jobs.id', ondelete='CASCADE'), nullable=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('stage_order', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('is_default', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'))
    )
    op.create_index('ix_recruitment_stages_id', 'recruitment_stages', ['id'])
    op.create_index('ix_recruitment_stages_job_id', 'recruitment_stages', ['job_id'])

    # Applications
    op.create_table(
        'applications',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('candidate_id', sa.Integer(), sa.ForeignKey('candidates.id', ondelete='CASCADE'), nullable=False),
        sa.Column('job_id', sa.Integer(), sa.ForeignKey('jobs.id', ondelete='SET NULL'), nullable=True),
        sa.Column('source', sa.String(), nullable=False, server_default='Direct'),
        sa.Column('current_stage_id', sa.Integer(), sa.ForeignKey('recruitment_stages.id', ondelete='SET NULL'), nullable=True),
        sa.Column('stage_name', sa.String(), nullable=False, server_default='Screening'),
        sa.Column('status', sa.String(), nullable=False, server_default='In Progress'),
        sa.Column('applied_date', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'))
    )
    op.create_index('ix_applications_id', 'applications', ['id'])
    op.create_index('ix_applications_candidate_id', 'applications', ['candidate_id'])
    op.create_index('ix_applications_job_id', 'applications', ['job_id'])

    # Interviews
    op.create_table(
        'interviews',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('application_id', sa.Integer(), sa.ForeignKey('applications.id', ondelete='CASCADE'), nullable=True),
        sa.Column('candidate_id', sa.Integer(), sa.ForeignKey('candidates.id', ondelete='CASCADE'), nullable=False),
        sa.Column('interviewer', sa.String(), nullable=False),
        sa.Column('scheduled_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('interview_type', sa.String(), nullable=False, server_default='Technical'),
        sa.Column('status', sa.String(), nullable=False, server_default='Scheduled'),
        sa.Column('meeting_link', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'))
    )
    op.create_index('ix_interviews_id', 'interviews', ['id'])
    op.create_index('ix_interviews_candidate_id', 'interviews', ['candidate_id'])
    op.create_index('ix_interviews_application_id', 'interviews', ['application_id'])

    # Interview Feedbacks
    op.create_table(
        'interview_feedbacks',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('interview_id', sa.Integer(), sa.ForeignKey('interviews.id', ondelete='CASCADE'), nullable=False),
        sa.Column('interviewer', sa.String(), nullable=False),
        sa.Column('feedback', sa.Text(), nullable=False),
        sa.Column('rating', sa.Float(), nullable=False),
        sa.Column('recommendation', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'))
    )
    op.create_index('ix_interview_feedbacks_id', 'interview_feedbacks', ['id'])
    op.create_index('ix_interview_feedbacks_interview_id', 'interview_feedbacks', ['interview_id'])

    # Assessments
    op.create_table(
        'assessments',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('assessment_type', sa.String(), nullable=False, server_default='Technical'),
        sa.Column('max_score', sa.Float(), nullable=False, server_default='100.0'),
        sa.Column('passing_score', sa.Float(), nullable=False, server_default='60.0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'))
    )
    op.create_index('ix_assessments_id', 'assessments', ['id'])
    op.create_index('ix_assessments_title', 'assessments', ['title'])

    # Assessment Results
    op.create_table(
        'assessment_results',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('assessment_id', sa.Integer(), sa.ForeignKey('assessments.id', ondelete='CASCADE'), nullable=False),
        sa.Column('candidate_id', sa.Integer(), sa.ForeignKey('candidates.id', ondelete='CASCADE'), nullable=False),
        sa.Column('application_id', sa.Integer(), sa.ForeignKey('applications.id', ondelete='CASCADE'), nullable=True),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('result', sa.String(), nullable=False, server_default='Pass'),
        sa.Column('feedback', sa.Text(), nullable=True),
        sa.Column('taken_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'))
    )
    op.create_index('ix_assessment_results_id', 'assessment_results', ['id'])
    op.create_index('ix_assessment_results_assessment_id', 'assessment_results', ['assessment_id'])
    op.create_index('ix_assessment_results_candidate_id', 'assessment_results', ['candidate_id'])

    # Offers
    op.create_table(
        'offers',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('candidate_id', sa.Integer(), sa.ForeignKey('candidates.id', ondelete='CASCADE'), nullable=False),
        sa.Column('application_id', sa.Integer(), sa.ForeignKey('applications.id', ondelete='CASCADE'), nullable=True),
        sa.Column('salary', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(), nullable=False, server_default='USD'),
        sa.Column('joining_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(), nullable=False, server_default='Draft'),
        sa.Column('sent_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('accepted_rejected_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'))
    )
    op.create_index('ix_offers_id', 'offers', ['id'])
    op.create_index('ix_offers_candidate_id', 'offers', ['candidate_id'])

    # Onboarding
    op.create_table(
        'onboarding',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('candidate_id', sa.Integer(), sa.ForeignKey('candidates.id', ondelete='CASCADE'), nullable=False),
        sa.Column('application_id', sa.Integer(), sa.ForeignKey('applications.id', ondelete='CASCADE'), nullable=True),
        sa.Column('joining_status', sa.String(), nullable=False, server_default='Pending'),
        sa.Column('document_verification', sa.String(), nullable=False, server_default='Pending'),
        sa.Column('background_check_status', sa.String(), nullable=False, server_default='Pending'),
        sa.Column('joining_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'))
    )
    op.create_index('ix_onboarding_id', 'onboarding', ['id'])
    op.create_index('ix_onboarding_candidate_id', 'onboarding', ['candidate_id'])

    # Communication History
    op.create_table(
        'communication_histories',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('candidate_id', sa.Integer(), sa.ForeignKey('candidates.id', ondelete='CASCADE'), nullable=False),
        sa.Column('sender', sa.String(), nullable=False),
        sa.Column('recipient', sa.String(), nullable=False),
        sa.Column('communication_type', sa.String(), nullable=False, server_default='Email'),
        sa.Column('subject', sa.String(), nullable=True),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('sent_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'))
    )
    op.create_index('ix_communication_histories_id', 'communication_histories', ['id'])
    op.create_index('ix_communication_histories_candidate_id', 'communication_histories', ['candidate_id'])

    # Activity Log
    op.create_table(
        'activity_logs',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('candidate_id', sa.Integer(), sa.ForeignKey('candidates.id', ondelete='SET NULL'), nullable=True),
        sa.Column('application_id', sa.Integer(), sa.ForeignKey('applications.id', ondelete='SET NULL'), nullable=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('performer', sa.String(), nullable=False),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'))
    )
    op.create_index('ix_activity_logs_id', 'activity_logs', ['id'])
    op.create_index('ix_activity_logs_candidate_id', 'activity_logs', ['candidate_id'])

    # Social Profiles
    op.create_table(
        'social_profiles',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('candidate_id', sa.Integer(), sa.ForeignKey('candidates.id', ondelete='CASCADE'), nullable=False),
        sa.Column('platform', sa.String(), nullable=False),
        sa.Column('profile_url', sa.String(), nullable=False),
        sa.Column('username', sa.String(), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('skills', sa.Text(), nullable=True),
        sa.Column('followers', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('repositories_count', sa.Integer(), nullable=True),
        sa.Column('top_languages', sa.Text(), nullable=True),
        sa.Column('total_stars', sa.Integer(), nullable=True),
        sa.Column('raw_data', sa.Text(), nullable=True),
        sa.Column('last_updated', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'))
    )
    op.create_index('ix_social_profiles_id', 'social_profiles', ['id'])
    op.create_index('ix_social_profiles_candidate_id', 'social_profiles', ['candidate_id'])
    op.create_index('ix_social_profiles_platform', 'social_profiles', ['platform'])

    # Candidate Source
    op.create_table(
        'candidate_sources',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('candidate_id', sa.Integer(), sa.ForeignKey('candidates.id', ondelete='CASCADE'), nullable=False),
        sa.Column('source_platform', sa.String(), nullable=False),
        sa.Column('source_url', sa.String(), nullable=True),
        sa.Column('recruiter', sa.String(), nullable=True),
        sa.Column('discovered_date', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'))
    )
    op.create_index('ix_candidate_sources_id', 'candidate_sources', ['id'])
    op.create_index('ix_candidate_sources_candidate_id', 'candidate_sources', ['candidate_id'])
    op.create_index('ix_candidate_sources_source_platform', 'candidate_sources', ['source_platform'])

    # Candidate Pipeline
    op.create_table(
        'candidate_pipelines',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('candidate_id', sa.Integer(), sa.ForeignKey('candidates.id', ondelete='CASCADE'), nullable=False),
        sa.Column('source', sa.String(), nullable=False),
        sa.Column('stage', sa.String(), nullable=False, server_default='Discovered'),
        sa.Column('recruiter', sa.String(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'))
    )
    op.create_index('ix_candidate_pipelines_id', 'candidate_pipelines', ['id'])
    op.create_index('ix_candidate_pipelines_candidate_id', 'candidate_pipelines', ['candidate_id'])

def downgrade() -> None:
    op.drop_table('candidate_pipelines')
    op.drop_table('candidate_sources')
    op.drop_table('social_profiles')
    op.drop_table('activity_logs')
    op.drop_table('communication_histories')
    op.drop_table('onboarding')
    op.drop_table('offers')
    op.drop_table('assessment_results')
    op.drop_table('assessments')
    op.drop_table('interview_feedbacks')
    op.drop_table('interviews')
    op.drop_table('applications')
    op.drop_table('recruitment_stages')
    op.drop_table('jobs')
