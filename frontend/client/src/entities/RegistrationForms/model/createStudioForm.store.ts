import { defineStore } from 'pinia';

type inputField = {
    name: string;
    title: string;
    type: string;
};

export type StudioFormValues = {
    logo: File | null;
    company: string;
    address: string;
    country: string;
    city: string;
    street: string;
    about: string;
    longitude: string;
    latitude: string;
    logo_preview: string | null;
};

type formValues = {
    inputValues: StudioFormValues;
    errors: string[];
    inputFields: inputField[];
};

export const useCreateStudioFormStore = defineStore('create-studio-store', {
    state: (): formValues => ({
        inputValues: {
            company: '',
            logo: null,
            logo_preview: null,
            about: '',
            address: '',
            country: '',
            city: '',
            street: '',
            longitude: '',
            latitude: '',
        },
        errors: [],
        inputFields: [
            { name: 'name', title: 'Name', type: 'text' },
            { name: 'email', title: 'Email', type: 'email' },
            { name: 'password', title: 'Password', type: 'password' },
            { name: 'password_confirmation', title: 'Confirm Password', type: 'password' }
        ]
    })
});