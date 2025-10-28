import { defineStore } from 'pinia';

export type inputField = {
    name: string;
    title: string;
    type: string;
}
export type inputValues = {
    name: string;
    email: string;
    password: string;
    password_confirmation: string;
    role: string;
}
export type formValues = {
    inputValues: inputValues
    errors: string[];
    inputFields: inputField[];
}

export const useCreateAccountFormStore = defineStore({
    id: 'create-account-store',
    state: (): formValues => ({
            inputValues: {
                name: '',
                email: '',
                password: '',
                password_confirmation: '',
                role: ''
            },
            errors: [],
            inputFields: [
                {name: 'name', title: 'Name', type: 'text'},
                {name: 'email', title: 'Email', type: 'email'},
                {name: 'password', title: 'Password', type: 'password'},
                {name: 'password_confirmation', title: 'Confirm Password', type: 'password'}]
    }),
    actions: {
        updateRole(role:string) {
            this.inputValues.role = role;
        },
    }
})