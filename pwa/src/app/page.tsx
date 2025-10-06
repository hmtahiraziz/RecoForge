'use client';

import { useQuery, useMutation } from '@apollo/client/react';
import { useState } from 'react';
import { PLButton } from './components/ui/PL/PLButton/PLButton';
import { PLInput } from './components/ui/PL/PLInput';

import SearchIcon from '@/app/icons/search.svg';
import { GET_QUESTIONNAIRES, CREATE_QUESTIONNAIRE, UPDATE_QUESTIONNAIRE, DELETE_QUESTIONNAIRE, GET_QUESTIONNAIRE, PUBLISH_QUESTIONNAIRE } from './lib/graphql/questionnaires.gql';
import { apolloClient } from './lib/graphql/apolloClient';

interface QuestionOption {
  id: string;
  value: string;
  label: string;
  orderIndex: number;
}

interface Question {
  id: string;
  key: string;
  type: string;
  label: string;
  required: boolean;
  orderIndex: number;
  options: QuestionOption[];
}

interface Questionnaire {
  id: string;
  categoryCode: string;
  title: string;
  description?: string;
  status: string;
  isActive: boolean;
  version: number;
  createdAt: string;
  updatedAt?: string;
  publishedAt?: string;
  questions?: Question[];
}

export default function Home() {
  const { data, loading, error } = useQuery<{ questionnaires: Questionnaire[] }>(GET_QUESTIONNAIRES);
  const [createQuestionnaire, { loading: creating }] = useMutation(CREATE_QUESTIONNAIRE, {
    refetchQueries: [{ query: GET_QUESTIONNAIRES }],
  });
  const [updateQuestionnaire, { loading: updating }] = useMutation(UPDATE_QUESTIONNAIRE, {
    refetchQueries: [{ query: GET_QUESTIONNAIRES }],
  });
  const [deleteQuestionnaire, { loading: deleting }] = useMutation(DELETE_QUESTIONNAIRE, {
    refetchQueries: [{ query: GET_QUESTIONNAIRES }],
  });
  const [publishQuestionnaire, { loading: publishing }] = useMutation(PUBLISH_QUESTIONNAIRE, {
    refetchQueries: [{ query: GET_QUESTIONNAIRES }],
  });

  // Predefined questionnaire types
  const questionnaireTypes = [
    { value: 'Bar', label: 'Bar' },
    { value: 'Club/RSL/Sports/Cinema', label: 'Club/RSL/Sports/Cinema' },
    { value: 'Events/Caterer', label: 'Events/Caterer' },
    { value: 'Hotel/Accommodation', label: 'Hotel/Accommodation' },
    { value: 'Pub', label: 'Pub' },
    { value: 'Restaurant', label: 'Restaurant' },
    { value: 'Retail/Off-Premise', label: 'Retail/Off-Premise' }
  ];

  // Form state
  const [formData, setFormData] = useState({
    categoryCode: '',
    title: '',
    description: '',
  });
  const [showForm, setShowForm] = useState(false);
  const [editingQuestionnaire, setEditingQuestionnaire] = useState<Questionnaire | null>(null);
  const [deleteConfirm, setDeleteConfirm] = useState<{ show: boolean; questionnaire: Questionnaire | null }>({
    show: false,
    questionnaire: null
  });

  // Get used types (excluding the current questionnaire being edited)
  const getUsedTypes = () => {
    if (!data?.questionnaires) return [];
    return data.questionnaires
      .filter(q => q.id !== editingQuestionnaire?.id)
      .map(q => q.categoryCode);
  };

  const usedTypes = getUsedTypes();

  // Search and filter state
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('');

  // Filter questionnaires based on search and filter
  const filteredQuestionnaires = data?.questionnaires?.filter(questionnaire => {
    const matchesSearch = searchTerm === '' || 
      questionnaire.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      questionnaire.categoryCode.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesFilter = filterType === '' || questionnaire.categoryCode === filterType;
    
    return matchesSearch && matchesFilter;
  }) || [];
  
  // Question state
  const [questions, setQuestions] = useState<any[]>([]);
  const [showQuestionForm, setShowQuestionForm] = useState(false);
  const [editingQuestionIndex, setEditingQuestionIndex] = useState<number | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState({
    type: 'SINGLE',
    label: '',
    required: false,
    orderIndex: 1,
    options: [] as Array<{value: string, orderIndex: number}>
  });

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-GB', {
      day: '2-digit',
      month: '2-digit',
      year: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusDisplay = (status: string, isActive: boolean) => {
    if (status === 'published' && isActive) return 'Active';
    if (status === 'published' && !isActive) return 'Published';
    if (status === 'draft') return 'Draft';
    if (status === 'archived') return 'Archived';
    return status;
  };

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingQuestionnaire) {
        // Update existing questionnaire
        await updateQuestionnaire({
          variables: {
            id: editingQuestionnaire.id,
            input: {
              title: formData.title,
              description: formData.description || null,
              questions: questions.length > 0 ? questions.map(q => ({
                key: q.key,
                type: q.type,
                label: q.label,
                required: q.required,
                orderIndex: q.orderIndex,
                options: q.options.map((opt: any) => ({
                  value: opt.value,
                  label: opt.label,
                  orderIndex: opt.orderIndex
                }))
              })) : null,
            }
          }
        });
        
        // Refetch the updated questionnaire to get the latest questions
        const { data: updatedData } = await apolloClient.query<{ questionnaire: Questionnaire }>({
          query: GET_QUESTIONNAIRE,
          variables: { id: editingQuestionnaire.id }
        });
        
        // Update the questions state with the fresh data
        if (updatedData?.questionnaire?.questions) {
          setQuestions(updatedData.questionnaire.questions.map((q: any) => ({
            key: q.key,
            type: q.type,
            label: q.label,
            required: q.required,
            orderIndex: q.orderIndex,
            options: q.options?.map((opt: any) => ({
              value: opt.value,
              label: opt.label,
              orderIndex: opt.orderIndex
            })) || []
          })));
        }
      } else {
        // Create new questionnaire
        await createQuestionnaire({
          variables: {
            input: {
              categoryCode: formData.categoryCode,
              title: formData.title,
              description: formData.description || null,
              questions: questions.length > 0 ? questions.map(q => ({
                key: q.key,
                type: q.type,
                label: q.label,
                required: q.required,
                orderIndex: q.orderIndex,
                options: q.options.map((opt: any) => ({
                  value: opt.value,
                  label: opt.label,
                  orderIndex: opt.orderIndex
                }))
              })) : undefined,
            }
          }
        });
      }
      // Reset form
      setFormData({ categoryCode: '', title: '', description: '' });
      setQuestions([]);
      setShowForm(false);
      setShowQuestionForm(false);
      setEditingQuestionnaire(null);
    } catch (error) {
      console.error('Error saving questionnaire:', error);
      
      // Check if it's a type uniqueness error
      if (error instanceof Error && error.message.includes('already exists')) {
        alert('A questionnaire with this type already exists. Please choose a different type.');
      } else {
        alert('Error saving questionnaire. Please try again.');
      }
    }
  };

  const handleEdit = async (questionnaire: Questionnaire) => {
    setEditingQuestionnaire(questionnaire);
    setFormData({
      categoryCode: questionnaire.categoryCode,
      title: questionnaire.title,
      description: questionnaire.description || '',
    });
    
    // Load questions for this questionnaire
    try {
      const { data: questionnaireData } = await apolloClient.query<{ questionnaire: Questionnaire }>({
        query: GET_QUESTIONNAIRE,
        variables: { id: questionnaire.id }
      });
      
      if (questionnaireData?.questionnaire?.questions) {
        const mappedQuestions = questionnaireData.questionnaire.questions.map((q: Question) => ({
          key: q.key,
          type: q.type,
          label: q.label,
          required: q.required,
          orderIndex: q.orderIndex,
          options: q.options ? q.options.map(opt => ({
            value: opt.value,
            label: opt.label,
            orderIndex: opt.orderIndex
          })) : []
        }));
        setQuestions(mappedQuestions);
      } else {
        setQuestions([]);
      }
    } catch (error) {
      console.error('Error loading questionnaire questions:', error);
      setQuestions([]);
    }
    
    setShowForm(true);
    setShowQuestionForm(false);
  };

  const handleDelete = async (questionnaire: Questionnaire) => {
    try {
      await deleteQuestionnaire({
        variables: { id: questionnaire.id }
      });
      setDeleteConfirm({ show: false, questionnaire: null });
    } catch (error) {
      console.error('Error deleting questionnaire:', error);
    }
  };

  const handlePublish = async (questionnaire: Questionnaire) => {
    try {
      await publishQuestionnaire({
        variables: { id: questionnaire.id }
      });
    } catch (error) {
      console.error('Error publishing questionnaire:', error);
      alert('Error publishing questionnaire: ' + (error as Error).message);
    }
  };

  const handleCancel = () => {
    setFormData({ categoryCode: '', title: '', description: '' });
    setQuestions([]);
    setShowForm(false);
    setShowQuestionForm(false);
    setEditingQuestionnaire(null);
  };

  // Question management functions
  const handleQuestionInputChange = (field: string, value: any) => {
    setCurrentQuestion(prev => ({ ...prev, [field]: value }));
  };

  const addOption = () => {
    setCurrentQuestion(prev => ({
      ...prev,
      options: [...prev.options, { value: '', orderIndex: prev.options.length + 1 }]
    }));
  };

  const updateOption = (index: number, field: string, value: string) => {
    setCurrentQuestion(prev => ({
      ...prev,
      options: prev.options.map((option, i) => 
        i === index ? { ...option, [field]: value } : option
      )
    }));
  };

  const removeOption = (index: number) => {
    setCurrentQuestion(prev => ({
      ...prev,
      options: prev.options.filter((_, i) => i !== index)
    }));
  };

  const addQuestion = () => {
    // Generate a key from the label (lowercase, replace spaces with underscores)
    const key = currentQuestion.label.toLowerCase().replace(/[^a-z0-9]/g, '_').replace(/_+/g, '_');
    
    const newQuestion = {
      ...currentQuestion,
      key: key,
      orderIndex: questions.length + 1,
      options: currentQuestion.options.filter(opt => opt.value).map(opt => ({
        value: opt.value,
        label: opt.value, // Use value as label
        orderIndex: opt.orderIndex
      }))
    };
    setQuestions(prev => [...prev, newQuestion]);
    setCurrentQuestion({
      type: 'SINGLE',
      label: '',
      required: false,
      orderIndex: questions.length + 2,
      options: []
    });
    // Close the form after adding a question
    setShowQuestionForm(false);
  };

  const editQuestion = (index: number) => {
    const question = questions[index];
    setEditingQuestionIndex(index);
    setCurrentQuestion({
      type: question.type,
      label: question.label,
      required: question.required,
      orderIndex: question.orderIndex,
      options: question.options.map((opt: any) => ({
        value: opt.value,
        orderIndex: opt.orderIndex
      }))
    });
    setShowQuestionForm(true);
  };

  const updateQuestion = () => {
    if (editingQuestionIndex === null) return;
    
    // Generate a key from the label (lowercase, replace spaces with underscores)
    const key = currentQuestion.label.toLowerCase().replace(/[^a-z0-9]/g, '_').replace(/_+/g, '_');
    
    const updatedQuestion = {
      ...currentQuestion,
      key: key,
      options: currentQuestion.options.filter(opt => opt.value).map(opt => ({
        value: opt.value,
        label: opt.value, // Use value as label
        orderIndex: opt.orderIndex
      }))
    };
    
    setQuestions(prev => prev.map((q, i) => i === editingQuestionIndex ? updatedQuestion : q));
    setCurrentQuestion({
      type: 'SINGLE',
      label: '',
      required: false,
      orderIndex: questions.length + 1,
      options: []
    });
    setEditingQuestionIndex(null);
    setShowQuestionForm(false);
  };

  const removeQuestion = (index: number) => {
    setQuestions(prev => prev.filter((_, i) => i !== index));
  };

  return (
    <main className="pt-16 flex flex-col items-center bg-surfacecolor-page min-h-screen">
      <div className="w-full flex flex-col lg:flex-row max-w-[1200px] lg:p-8 lg:gap-6">
        {/* Left side - Questionnaire List */}
        <div className="w-full flex flex-col max-w-[400px] lg:max-w-[600px]">
        <div className="flex flex-col gap-4 p-4 lg:p-0">
          <h1 className="text-heading-xl text-textcolor-primary text-left w-full">Questionnaires</h1>
          <PLButton 
            hierarchy="primary" 
            onClick={() => setShowForm(!showForm)}
          >
            {showForm ? 'Cancel' : 'Create questionnaire'}
          </PLButton>
        </div>
        <div className="p-4 shadow-sm flex gap-4 items-center lg:rounded-md bg-surfacecolor-primary">
          <PLInput 
            leadingIcon={<SearchIcon />} 
            placeholder="Search by title or type..." 
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <select
            className="p-2 border border-gray-300 rounded-md text-body-xs text-textcolor-primary bg-surfacecolor-primary focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
          >
            <option value="">All Types</option>
            {questionnaireTypes.map((type) => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </select>
          {(searchTerm || filterType) && (
            <button 
              className="text-textcolor-action text-body-xs-link hover:underline"
              onClick={() => {
                setSearchTerm('');
                setFilterType('');
              }}
            >
              Clear Filters
            </button>
          )}
        </div>
        <div className="flex flex-col gap-1">
          <div className="px-4 py-2 bg-surfacecolor-primary shadow-sm lg:rounded-md flex flex-items-center">
            <span className="text-textcolor-secondary text-heading-xs">Questionnaires</span>
          </div>
          
          {loading && (
            <div className="p-4 bg-surfacecolor-primary shadow-sm lg:rounded-md">
              <span className="text-textcolor-secondary text-body-xs">Loading questionnaires...</span>
            </div>
          )}
          
          {error && (
            <div className="p-4 bg-surfacecolor-primary shadow-sm lg:rounded-md">
              <span className="text-red-500 text-body-xs">Error loading questionnaires: {error.message}</span>
            </div>
          )}
          
          {filteredQuestionnaires.length === 0 && !loading && (
            <div className="p-4 bg-surfacecolor-primary shadow-sm lg:rounded-md">
              <span className="text-textcolor-secondary text-body-xs">
                {searchTerm || filterType ? 'No questionnaires match your search/filter' : 'No questionnaires found'}
              </span>
            </div>
          )}
          
          {filteredQuestionnaires.map((questionnaire: Questionnaire) => (
            <div key={questionnaire.id} className="p-4 flex flex-col bg-surfacecolor-primary shadow-sm gap-2 lg:rounded-md">
              <div className="flex gap-2">
                <span className="text-textcolor-primary text-body-xs">{questionnaire.title}</span>
                <div className="bg-surfacecolor-tertiary rounded-full h-[18px] flex items-center justify-center px-2 py-[3px]">
                  <span className="text-textcolor-primary text-body-xxs">
                    {getStatusDisplay(questionnaire.status, questionnaire.isActive)}
                  </span>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div className="flex flex-col">
                  <span className="text-textcolor-secondary text-heading-xs">Type</span>
                  <span className="text-textcolor-primary text-body-xs">{questionnaire.categoryCode}</span>
                </div>
                <div className="flex flex-col">
                  <span className="text-textcolor-secondary text-heading-xs">Status</span>
                  <span className="text-textcolor-primary text-body-xs">{questionnaire.status}</span>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div className="flex flex-col">
                  <span className="text-textcolor-secondary text-heading-xs">Last updated</span>
                  <span className="text-textcolor-primary text-body-xs">
                    {questionnaire.updatedAt ? formatDate(questionnaire.updatedAt) : formatDate(questionnaire.createdAt)}
                  </span>
                </div>
                <div className="flex flex-col">
                  <span className="text-textcolor-secondary text-heading-xs">Created on</span>
                  <span className="text-textcolor-primary text-body-xs">{formatDate(questionnaire.createdAt)}</span>
                </div>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex gap-2">
                  <button 
                    onClick={() => handleEdit(questionnaire)}
                    className="text-textcolor-action text-body-xs-link hover:underline"
                  >
                    Edit
                  </button>
                  {questionnaire.status === 'DRAFT' && (
                    <button 
                      onClick={() => setDeleteConfirm({ show: true, questionnaire })}
                      className="text-red-500 text-body-xs-link hover:underline"
                    >
                      Delete
                    </button>
                  )}
                </div>
                
                {/* Publish Button - only for drafts */}
                {questionnaire.status === 'DRAFT' && (
                  <button
                    onClick={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      handlePublish(questionnaire);
                    }}
                    disabled={publishing}
                    className="bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white px-3 py-1.5 rounded text-xs font-medium transition-colors cursor-pointer disabled:cursor-not-allowed"
                  >
                    {publishing ? 'Publishing...' : 'Publish'}
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
        </div>

        {/* Create Questionnaire Form */}
        {showForm && (
          <div className="w-full flex flex-col max-w-[400px] lg:max-w-[500px]">
            <div className="flex flex-col gap-4 p-4 lg:p-0">
              <h2 className="text-heading-lg text-textcolor-primary text-left w-full">
                {editingQuestionnaire ? 'Edit Questionnaire' : 'Create New Questionnaire'}
              </h2>
              
              <form onSubmit={handleSubmit} className="flex flex-col gap-4">
                <div className="flex flex-col gap-2">
                  <label className="text-textcolor-primary text-body-xs">Type</label>
                  <select
                    className="p-3 border border-gray-300 rounded-md text-body-xs text-textcolor-primary bg-surfacecolor-primary focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
                    value={formData.categoryCode}
                    onChange={(e) => handleInputChange('categoryCode', e.target.value)}
                    required
                    disabled={!!editingQuestionnaire}
                  >
                    <option value="">Select a type...</option>
                    {questionnaireTypes.map((type) => {
                      const isUsed = usedTypes.includes(type.value);
                      return (
                        <option 
                          key={type.value} 
                          value={type.value}
                          disabled={isUsed}
                          className={isUsed ? 'text-gray-400' : ''}
                        >
                          {type.label} {isUsed ? '(Already used)' : ''}
                        </option>
                      );
                    })}
                  </select>
                </div>
                
                <div className="flex flex-col gap-2">
                  <label className="text-textcolor-primary text-body-xs">Title</label>
                  <PLInput
                    placeholder="Enter questionnaire title"
                    value={formData.title}
                    onChange={(e) => handleInputChange('title', e.target.value)}
                    required
                  />
                </div>
                
                <div className="flex flex-col gap-2">
                  <label className="text-textcolor-primary text-body-xs">Description (Optional)</label>
                  <textarea
                    className="p-3 border border-gray-300 rounded-md text-body-xs text-textcolor-primary bg-surfacecolor-primary focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter questionnaire description"
                    value={formData.description}
                    onChange={(e) => handleInputChange('description', e.target.value)}
                    rows={3}
                  />
                </div>

                {/* Questions Section */}
                <div className="flex flex-col gap-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-textcolor-primary text-body-sm">Questions ({questions.length})</h3>
                    <PLButton 
                      type="button" 
                      hierarchy="secondary" 
                      onClick={() => setShowQuestionForm(!showQuestionForm)}
                    >
                      {showQuestionForm ? 'Cancel' : 'Add Question'}
                    </PLButton>
                  </div>

                  {/* Question Form */}
                  {showQuestionForm && (
                    <div className="p-4 border border-gray-200 rounded-md bg-gray-50">
                      <div className="flex flex-col gap-4">
                        <h4 className="text-textcolor-primary text-body-sm font-medium">
                          {editingQuestionIndex !== null ? 'Edit Question' : 'Add New Question'}
                        </h4>
                        <div className="flex flex-col gap-2">
                          <label className="text-textcolor-primary text-body-xs">Question Title</label>
                          <PLInput
                            placeholder="Enter question title"
                            value={currentQuestion.label}
                            onChange={(e) => handleQuestionInputChange('label', e.target.value)}
                            required
                          />
                        </div>

                        <div className="flex flex-col gap-2">
                          <label className="text-textcolor-primary text-body-xs">Question Type</label>
                          <select
                            className="p-3 border border-gray-300 rounded-md text-body-xs text-textcolor-primary bg-surfacecolor-primary focus:outline-none focus:ring-2 focus:ring-blue-500"
                            value={currentQuestion.type}
                            onChange={(e) => handleQuestionInputChange('type', e.target.value)}
                          >
                            <option value="SINGLE">Single Choice (Radio buttons)</option>
                            <option value="MULTI">Multiple Choice (Checkboxes)</option>
                          </select>
                        </div>

                        <div className="flex items-center gap-2">
                          <input
                            type="checkbox"
                            id="required"
                            checked={currentQuestion.required}
                            onChange={(e) => handleQuestionInputChange('required', e.target.checked)}
                            className="rounded"
                          />
                          <label htmlFor="required" className="text-textcolor-primary text-body-xs">
                            Required question
                          </label>
                        </div>

                        {/* Options Section */}
                        <div className="flex flex-col gap-2">
                          <div className="flex items-center justify-between">
                            <div className="flex flex-col gap-1">
                              <label className="text-textcolor-primary text-body-xs">Answer Options</label>
                              <span className="text-textcolor-secondary text-body-xxs">
                                Minimum 2 options required
                              </span>
                            </div>
                            <button 
                              type="button" 
                              onClick={addOption}
                              className="text-textcolor-action text-body-xs-link hover:underline"
                            >
                              + Add Option
                            </button>
                          </div>

                          {currentQuestion.options.map((option, index) => (
                            <div key={index} className="flex gap-2 items-center">
                              <PLInput
                                placeholder="Option text (e.g., Excellent)"
                                value={option.value}
                                onChange={(e) => updateOption(index, 'value', e.target.value)}
                                className="flex-1"
                              />
                              <button 
                                type="button" 
                                onClick={() => removeOption(index)}
                                className="text-red-500 text-body-xs hover:underline"
                              >
                                Remove
                              </button>
                            </div>
                          ))}
                        </div>

                        <div className="flex gap-2">
                          <PLButton 
                            type="button" 
                            hierarchy="primary" 
                            onClick={editingQuestionIndex !== null ? updateQuestion : addQuestion}
                            disabled={!currentQuestion.label || currentQuestion.options.filter(opt => opt.value).length < 2}
                          >
                            {editingQuestionIndex !== null ? 'Update Question' : 'Add Question'}
                          </PLButton>
                          <PLButton 
                            type="button" 
                            hierarchy="secondary" 
                            onClick={() => {
                              setShowQuestionForm(false);
                              setEditingQuestionIndex(null);
                              setCurrentQuestion({
                                type: 'SINGLE',
                                label: '',
                                required: false,
                                orderIndex: questions.length + 1,
                                options: []
                              });
                            }}
                          >
                            Cancel
                          </PLButton>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Questions List */}
                  {questions.length > 0 ? (
                    <div className="flex flex-col gap-2">
                      {questions.map((question, index) => (
                        <div key={index} className="p-3 border border-gray-200 rounded-md bg-white">
                          <div className="flex items-center justify-between">
                            <div className="flex flex-col gap-1">
                              <span className="text-textcolor-primary text-body-xs font-medium">
                                {question.label}
                              </span>
                              <span className="text-textcolor-secondary text-body-xxs">
                                {question.type} • {question.required ? 'Required' : 'Optional'} • {question.options?.length || 0} options
                              </span>
                            </div>
                            <div className="flex gap-2">
                              <button 
                                type="button" 
                                onClick={() => editQuestion(index)}
                                className="text-textcolor-action text-body-xs-link hover:underline"
                              >
                                Edit
                              </button>
                              <button 
                                type="button" 
                                onClick={() => removeQuestion(index)}
                                className="text-red-500 text-body-xs-link hover:underline"
                              >
                                Remove
                              </button>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="p-3 border border-gray-200 rounded-md bg-gray-50">
                      <span className="text-textcolor-secondary text-body-xs">
                        No questions added yet. Click &quot;Add Question&quot; to get started.
                      </span>
                    </div>
                  )}
                </div>
                
                <div className="flex gap-2">
                  <PLButton 
                    type="submit" 
                    hierarchy="primary" 
                    disabled={creating || updating}
                  >
                    {creating ? 'Creating...' : updating ? 'Updating...' : editingQuestionnaire ? 'Update Questionnaire' : 'Create Questionnaire'}
                  </PLButton>
                  <PLButton 
                    type="button" 
                    hierarchy="secondary" 
                    onClick={handleCancel}
                  >
                    Cancel
                  </PLButton>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>

      {/* Delete Confirmation Modal */}
      {deleteConfirm.show && deleteConfirm.questionnaire && (
        <div className="fixed inset-0 bg-black bg-opacity-20 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg max-w-md w-full mx-4">
            <h3 className="text-heading-md text-textcolor-primary mb-4">Delete Questionnaire</h3>
            <p className="text-textcolor-secondary text-body-sm mb-6">
              Are you sure you want to delete &quot;{deleteConfirm.questionnaire.title}&quot;? This action cannot be undone.
            </p>
            <div className="flex gap-3 justify-end">
              <PLButton 
                hierarchy="secondary" 
                onClick={() => setDeleteConfirm({ show: false, questionnaire: null })}
                disabled={deleting}
              >
                Cancel
              </PLButton>
              <PLButton 
                hierarchy="primary" 
                onClick={() => handleDelete(deleteConfirm.questionnaire!)}
                disabled={deleting}
              >
                {deleting ? 'Deleting...' : 'Delete'}
              </PLButton>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
