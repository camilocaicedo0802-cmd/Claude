"use client";

import { useUI } from "@/components/shell/ui-context";
import { TransactionForm } from "./transaction-form";
import {
  AccountForm,
  BudgetForm,
  CategoryForm,
  ContributionForm,
  GoalForm,
  ObligationForm,
  ObligationPaymentForm,
  PlannedIncomeForm,
  ReceiveIncomeForm,
} from "./finance-forms";
import { ClientForm, JobForm, PaymentForm } from "./client-forms";
import { EventForm, HabitForm, TaskForm } from "./life-forms";

/** Renders whichever form is requested through useUI().openForm(). One form at a time. */
export function FormHost() {
  const { form, closeForm } = useUI();
  if (!form) return null;
  const key = JSON.stringify(form);
  const done = closeForm;
  switch (form.kind) {
    case "transaction":
      return <TransactionForm key={key} id={form.id} defaults={form.defaults} onDone={done} />;
    case "account":
      return <AccountForm key={key} id={form.id} defaultType={form.defaults?.type} onDone={done} />;
    case "obligation":
      return <ObligationForm key={key} id={form.id} onDone={done} />;
    case "obligationPayment":
      return <ObligationPaymentForm key={key} obligationId={form.obligationId} dueDate={form.dueDate} onDone={done} />;
    case "plannedIncome":
      return <PlannedIncomeForm key={key} id={form.id} onDone={done} />;
    case "receiveIncome":
      return <ReceiveIncomeForm key={key} plannedIncomeId={form.plannedIncomeId} dueDate={form.dueDate} onDone={done} />;
    case "budget":
      return <BudgetForm key={key} categoryId={form.categoryId} onDone={done} />;
    case "category":
      return <CategoryForm key={key} id={form.id} defaultKind={form.defaults?.kind} onDone={done} />;
    case "goal":
      return <GoalForm key={key} id={form.id} onDone={done} />;
    case "contribution":
      return <ContributionForm key={key} goalId={form.goalId} onDone={done} />;
    case "client":
      return <ClientForm key={key} id={form.id} onDone={done} />;
    case "job":
      return <JobForm key={key} id={form.id} defaults={form.defaults} onDone={done} />;
    case "payment":
      return <PaymentForm key={key} id={form.id} defaults={form.defaults} onDone={done} />;
    case "task":
      return <TaskForm key={key} id={form.id} defaults={form.defaults} onDone={done} />;
    case "event":
      return <EventForm key={key} id={form.id} occurrence={form.occurrence} defaults={form.defaults} onDone={done} />;
    case "habit":
      return <HabitForm key={key} id={form.id} onDone={done} />;
  }
}
