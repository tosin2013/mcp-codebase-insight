import React from 'react';
import { Calendar, MapPin, Globe2, Users } from 'lucide-react';
import type { TechEvent } from '../../types';

interface TechEventsProps {
  events: TechEvent[];
}

export function TechEvents({ events }: TechEventsProps) {
  return (
    <div className="bg-white py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h2 className="text-3xl font-extrabold text-gray-900 sm:text-4xl">
            Upcoming Tech Events
          </h2>
          <p className="mt-3 max-w-2xl mx-auto text-xl text-gray-500 sm:mt-4">
            Join the tech community at these upcoming events, conferences, and meetups.
          </p>
        </div>

        <div className="mt-12 grid gap-8 md:grid-cols-2 lg:grid-cols-3">
          {events.map((event) => (
            <div
              key={event.id}
              className="flex flex-col bg-white rounded-lg shadow-lg overflow-hidden hover:shadow-xl transition-shadow"
            >
              <div className="flex-1 p-6">
                <div className="flex items-center justify-between">
                  <h3 className="text-xl font-semibold text-gray-900">{event.title}</h3>
                  {event.isVirtual && (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      Virtual
                    </span>
                  )}
                </div>

                <p className="mt-3 text-base text-gray-500 line-clamp-3">
                  {event.description}
                </p>

                <div className="mt-6 space-y-2">
                  <div className="flex items-center text-sm text-gray-500">
                    <Calendar className="h-4 w-4 mr-2" />
                    {new Date(event.eventDate).toLocaleDateString(undefined, {
                      weekday: 'long',
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric',
                    })}
                  </div>

                  <div className="flex items-center text-sm text-gray-500">
                    {event.isVirtual ? (
                      <>
                        <Globe2 className="h-4 w-4 mr-2" />
                        Online Event
                      </>
                    ) : (
                      <>
                        <MapPin className="h-4 w-4 mr-2" />
                        {event.location}
                      </>
                    )}
                  </div>

                  <div className="flex items-center text-sm text-gray-500">
                    <Users className="h-4 w-4 mr-2" />
                    {event.organizer}
                  </div>
                </div>
              </div>

              {event.url && (
                <div className="px-6 py-4 bg-gray-50 border-t border-gray-100">
                  <a
                    href={event.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-base font-medium text-indigo-600 hover:text-indigo-500"
                  >
                    Learn more about this event →
                  </a>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}