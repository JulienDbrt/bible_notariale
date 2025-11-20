'use client';

import { useState } from 'react';
import { ThumbsUp, ThumbsDown, MessageCircle, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent } from '@/components/ui/card';
import { useToast } from '@/hooks/use-toast';
import { evaluationsApi } from '@/lib/api';

interface EvaluationComponentProps {
  messageId: string;
  conversationId: string;
  initialEvaluation?: {
    id: string;
    evaluation_type: 'positive' | 'negative';
    comment?: string;
  };
  onEvaluationChange?: (evaluation: {
    id: string;
    evaluation_type: 'positive' | 'negative';
    comment?: string;
  } | null) => void;
  compact?: boolean;
}

export default function EvaluationComponent({
  messageId,
  conversationId,
  initialEvaluation,
  onEvaluationChange,
  compact = false
}: EvaluationComponentProps) {
  const [currentEvaluation, setCurrentEvaluation] = useState(initialEvaluation);
  const [isEditing, setIsEditing] = useState(false);
  const [comment, setComment] = useState(initialEvaluation?.comment || '');
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  const handleEvaluate = async (type: 'positive' | 'negative') => {
    // If clicking negative, always show comment box first
    if (type === 'negative' && !currentEvaluation) {
      setIsEditing(true);
      setComment('');
      return;
    }

    // If updating existing negative evaluation, show comment box
    if (type === 'negative' && currentEvaluation && currentEvaluation.evaluation_type !== 'negative') {
      setIsEditing(true);
      setComment(currentEvaluation?.comment || '');
      return;
    }

    // For positive evaluation, submit directly
    if (type === 'positive') {
      await submitEvaluation(type);
    } else if (type === 'negative' && comment.trim()) {
      // For negative with existing comment, submit
      await submitEvaluation(type);
    } else if (type === 'negative') {
      // This shouldn't happen with the new flow, but just in case
      toast({
        title: 'Comment Required',
        description: 'Please provide a comment for negative feedback.',
        variant: 'destructive',
      });
    }
  };

  const submitEvaluation = async (type: 'positive' | 'negative') => {
    setIsLoading(true);
    try {
      const evaluationData = {
        conversation_id: conversationId,
        message_id: messageId,
        evaluation_type: type,
        comment: type === 'negative' ? comment.trim() : null,
      };

      let result;
      if (currentEvaluation) {
        // Update existing evaluation
        result = await evaluationsApi.update(currentEvaluation.id, {
          evaluation_type: type,
          comment: type === 'negative' ? comment.trim() : null,
        });
      } else {
        // Create new evaluation
        result = await evaluationsApi.create(evaluationData);
      }

      const simplifiedResult = {
        id: result.id,
        evaluation_type: result.evaluation_type,
        comment: result.comment || undefined
      };
      setCurrentEvaluation(simplifiedResult);
      setIsEditing(false);
      
      if (onEvaluationChange) {
        onEvaluationChange(simplifiedResult);
      }

      toast({
        title: 'Evaluation Saved',
        description: `Thank you for your ${type} feedback!`,
      });

    } catch (error) {
      console.error('Evaluation error:', error);
      toast({
        title: 'Evaluation Failed',
        description: (error as Error).message || 'Failed to save evaluation',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!currentEvaluation) return;
    
    setIsLoading(true);
    try {
      await evaluationsApi.delete(currentEvaluation.id);
      setCurrentEvaluation(undefined);
      setIsEditing(false);
      setComment('');
      
      if (onEvaluationChange) {
        onEvaluationChange(null);
      }

      toast({
        title: 'Evaluation Deleted',
        description: 'Your feedback has been removed.',
      });
    } catch (error) {
      console.error('Delete evaluation error:', error);
      toast({
        title: 'Delete Failed',
        description: 'Failed to delete evaluation',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const cancelEdit = () => {
    setIsEditing(false);
    setComment(currentEvaluation?.comment || '');
  };

  if (compact && !isEditing) {
    return (
      <div className="flex items-center gap-1 ml-auto">
        <Button
          variant="ghost"
          size="sm"
          className={`h-6 w-6 p-0 ${currentEvaluation?.evaluation_type === 'positive' ? 'text-green-600 bg-green-50' : 'text-muted-foreground hover:text-green-600'}`}
          onClick={() => handleEvaluate('positive')}
          disabled={isLoading}
        >
          <ThumbsUp className="h-3 w-3" />
        </Button>
        <Button
          variant="ghost"
          size="sm"
          className={`h-6 w-6 p-0 ${currentEvaluation?.evaluation_type === 'negative' ? 'text-red-600 bg-red-50' : 'text-muted-foreground hover:text-red-600'}`}
          onClick={() => handleEvaluate('negative')}
          disabled={isLoading}
        >
          <ThumbsDown className="h-3 w-3" />
        </Button>
        {currentEvaluation && (
          <Button
            variant="ghost"
            size="sm"
            className="h-6 w-6 p-0 text-muted-foreground hover:text-red-600"
            onClick={handleDelete}
            disabled={isLoading}
          >
            <X className="h-3 w-3" />
          </Button>
        )}
      </div>
    );
  }

  // When in compact mode but editing (showing comment box)
  if (compact && isEditing) {
    return (
      <div className="w-full max-w-sm">
        <Card className="mt-2">
          <CardContent className="p-3">
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <MessageCircle className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm font-medium">Please tell us how we can improve:</span>
              </div>
              <Textarea
                placeholder="Your feedback helps us improve..."
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                className="min-h-[60px] resize-none text-sm"
              />
              <div className="flex gap-2">
                <Button
                  size="sm"
                  onClick={() => submitEvaluation('negative')}
                  disabled={isLoading || !comment.trim()}
                  className="text-xs"
                >
                  {isLoading ? 'Saving...' : 'Submit Feedback'}
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={cancelEdit}
                  disabled={isLoading}
                  className="text-xs"
                >
                  Cancel
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <span className="text-sm text-muted-foreground">How was this response?</span>
        <div className="flex gap-1">
          <Button
            variant="outline"
            size="sm"
            className={`${currentEvaluation?.evaluation_type === 'positive' ? 'bg-green-50 text-green-600 border-green-200' : ''}`}
            onClick={() => handleEvaluate('positive')}
            disabled={isLoading}
          >
            <ThumbsUp className="h-4 w-4 mr-1" />
            Good
          </Button>
          <Button
            variant="outline"
            size="sm"
            className={`${currentEvaluation?.evaluation_type === 'negative' ? 'bg-red-50 text-red-600 border-red-200' : ''}`}
            onClick={() => handleEvaluate('negative')}
            disabled={isLoading}
          >
            <ThumbsDown className="h-4 w-4 mr-1" />
            Needs Improvement
          </Button>
          {currentEvaluation && (
            <Button
              variant="ghost"
              size="sm"
              onClick={handleDelete}
              disabled={isLoading}
              className="text-muted-foreground hover:text-red-600"
            >
              <X className="h-4 w-4" />
            </Button>
          )}
        </div>
      </div>

      {/* Comment Section */}
      {(isEditing || currentEvaluation?.comment) && (
        <Card className="mt-3">
          <CardContent className="p-3">
            {isEditing ? (
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <MessageCircle className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm font-medium">
                    {currentEvaluation?.evaluation_type === 'negative' || !currentEvaluation 
                      ? 'Please tell us how we can improve:' 
                      : 'Update your comment:'
                    }
                  </span>
                </div>
                <Textarea
                  placeholder="Your feedback helps us improve..."
                  value={comment}
                  onChange={(e) => setComment(e.target.value)}
                  className="min-h-[80px] resize-none"
                />
                <div className="flex gap-2">
                  <Button
                    size="sm"
                    onClick={() => submitEvaluation(currentEvaluation?.evaluation_type || 'negative')}
                    disabled={isLoading || (currentEvaluation?.evaluation_type === 'negative' && !comment.trim())}
                  >
                    {isLoading ? 'Saving...' : 'Save Feedback'}
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={cancelEdit}
                    disabled={isLoading}
                  >
                    Cancel
                  </Button>
                </div>
              </div>
            ) : (
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <MessageCircle className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm font-medium">Your feedback:</span>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setIsEditing(true)}
                    disabled={isLoading}
                    className="text-xs"
                  >
                    Edit
                  </Button>
                </div>
                <p className="text-sm text-muted-foreground pl-6">
                  {currentEvaluation?.comment}
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}